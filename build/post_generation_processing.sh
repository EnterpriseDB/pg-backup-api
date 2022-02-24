#!/usr/bin/env bash

# Basic unsafe script for post processing generated files

replace_import_path(){
 # prepend `pg_backup_api` to `openapi_server` in autogenerated imports
 # For example, `from openapi_server.models.diagnose_output import DiagnoseOutput`
 # needs to become `from pg_backup_api.openapi_server.models.diagnose_output import DiagnoseOutput`.
 # In future we may be able to figure out how get the generator to do this for us,
 # but for now it seems like we'd need to fork the generator code itself, as these imports are pre-computed before
 # they get passed to the template.
  sed -i 's/from openapi_server/from pg_backup_api.openapi_server/g' $1
}

main(){
file_path=$1
echo "Post processing ${file_path}"

echo "Replace_import_path in ${file_path}"
replace_import_path ${file_path}

echo "Apply black for ${file_path}"
black ${file_path}
# Todo: Remove unused imports (ie duplicates)
}

main $1