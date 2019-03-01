export PROJECT_NAMESPACE="l4ygcl"
export PROJECT_OS_DIR=${PROJECT_OS_DIR:-../../openshift}

export GIT_URI="https://github.com/saravankumarpa/sbc-auth.git"
export GIT_REF="master"

# The templates that should not have their GIT referances(uri and ref) over-ridden
# Templates NOT in this list will have they GIT referances over-ridden
# with the values of GIT_URI and GIT_REF
export -a skip_git_overrides=""

# The project components
# - They are all  under the main OpenShift folder.
export components="auth-api auth-web"

# The builds to be triggered after buildconfigs created (not auto-triggered)
export builds=""

# The images to be tagged after build
export images="auth-api auth-web"

# The routes for the project
export routes="auth-web"
