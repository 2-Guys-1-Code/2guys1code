/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  'extends': [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier/skip-formatting'
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    "sort-imports": ["error", {
      "ignoreCase": true,
      "ignoreDeclarationSort": false,
      "ignoreMemberSort": false,
      "memberSyntaxSortOrder": ["none", "all", "multiple", "single"],
      "allowSeparatedGroups": false
    }]
  }

}
