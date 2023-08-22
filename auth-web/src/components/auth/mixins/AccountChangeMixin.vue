<script lang="ts">
import Component from 'vue-class-component'
import Vue from 'vue'

@Component({
  name: 'AccountChangeMixin'
})
export default class AccountChangeMixin extends Vue {
  protected unregisterHandler: () => void

  protected setAccountChangedHandler (handler: () => any) {
    // TODO: FIX THIS
    this.unregisterHandler = this.$store.subscribe((mutation) => {
      if (mutation.type === 'org/setCurrentOrganization') {
        handler()
      }
    })
  }

  protected beforeDestroy () {
    this.unregisterHandler && this.unregisterHandler()
  }
}
</script>
