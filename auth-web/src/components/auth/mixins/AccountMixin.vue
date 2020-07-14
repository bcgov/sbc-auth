// You can declare a mixin as the same style as components.
<script lang="ts">
import { AccountSettings } from '@/models/account-settings'
import Component from 'vue-class-component'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'
import Vue from 'vue'
@Component({
  computed: {
  },
  methods: {
  }
})
export default class AccountMixin extends Vue {
  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }
}
</script>
