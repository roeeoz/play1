project_version() {
    local repo_root
    repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    sed -n 's/^version = "\(.*\)"/\1/p' "${repo_root}/pyproject.toml"
}
