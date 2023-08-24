<script lang="ts">
import Component from 'vue-class-component'
import Vue from 'vue'
import { useOrgStore } from '@/store/org'

@Component({
  name: 'AccountChangeMixin'
})
export default class AccountChangeMixin extends Vue {
  protected unregisterHandler: () => void

  protected setAccountChangedHandler (handler: () => any) {
    this.unregisterHandler = useOrgStore().$onAction(({ name, after }) => {
      after(() => {
        if (['syncOrganization', 'setCurrentOrganization'].includes(name)) {
          handler()
        }
      })
    })
  }

  protected beforeDestroy () {
    this.unregisterHandler && this.unregisterHandler()
  }
}
</script>
