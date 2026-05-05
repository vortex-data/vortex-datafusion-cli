// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: Copyright the Vortex contributors

use std::fs;
use std::path::Path;
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

#[test]
fn cli_writes_and_reads_vortex_with_sql() {
    let temp_dir = TempDir::new();
    let data_dir = temp_dir.path().join("events");
    let script_path = temp_dir.path().join("query.sql");

    fs::write(
        &script_path,
        format!(
            "\
COPY (SELECT * FROM (VALUES (1, 'alpha'), (2, 'beta'), (3, 'gamma')) AS t(id, label)) TO '{target_dir}' STORED AS VORTEX;
CREATE EXTERNAL TABLE events STORED AS VORTEX LOCATION '{target_dir}';
SELECT COUNT(*) AS n, SUM(id) AS total FROM events WHERE label <> 'beta';
",
            target_dir = sql_path(&data_dir),
        ),
    )
    .expect("write SQL script");

    let output = Command::new(env!("CARGO_BIN_EXE_vortex-datafusion-cli"))
        .args(["--quiet", "--file"])
        .arg(&script_path)
        .output()
        .expect("run vortex-datafusion-cli");

    assert!(
        output.status.success(),
        "CLI failed with status {:?}\nstdout:\n{}\nstderr:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr),
    );

    let stdout = String::from_utf8_lossy(&output.stdout);
    insta::assert_snapshot!(stdout.as_ref(), @r"
        +-------+
        | count |
        +-------+
        | 3     |
        +-------+
        +---+-------+
        | n | total |
        +---+-------+
        | 2 | 4     |
        +---+-------+
");
}

fn sql_path(path: &Path) -> String {
    path.to_string_lossy().replace('\'', "''")
}

struct TempDir {
    path: std::path::PathBuf,
}

impl TempDir {
    fn new() -> Self {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock before Unix epoch")
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "vortex-datafusion-cli-test-{}-{unique}",
            std::process::id()
        ));
        fs::create_dir(&path).expect("create temp dir");
        Self { path }
    }

    fn path(&self) -> &Path {
        &self.path
    }
}

impl Drop for TempDir {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.path);
    }
}
