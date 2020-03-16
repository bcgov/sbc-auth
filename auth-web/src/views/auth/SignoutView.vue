<template>
  <sbc-signout :redirect-url="redirectUrl"></sbc-signout>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'

@Component({
  methods: {
  },
  components: {
    SbcSignout
  }
})

export default class SignoutView extends Vue {
  @Prop() redirectUrl: string

  async mounted () {
    this.$store.replaceState({})
  }
}
</script>

<style lang="scss" scoped>
</style>
