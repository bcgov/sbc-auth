<template>
  <SbcAuthenticationOptions
    :in-auth="true"
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import SbcAuthenticationOptions from 'sbc-common-components/src/components/SbcAuthenticationOptions.vue'

@Component({
  components: {
    SbcAuthenticationOptions
  }
})
export default class AuthenticationOptionsView extends Vue {
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
</style>
