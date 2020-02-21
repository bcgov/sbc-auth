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
  @import '$assets/scss/theme.scss';

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    z-index: 2;
    background: $gray2;
  }
</style>
