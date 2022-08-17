<template>
  <v-btn large outlined color="bcgovblue"
    class="learn-more-btn font-weight-bold"
    :class="{'px-8': isWide}"
    :href="redirectUrl"
    target="_blank" rel="noopener noreferrer">
    Learn More
  </v-btn>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class LearnMoreButton extends Vue {
  @Prop() redirectUrl: string

  @Prop({ default: false }) isWide: boolean
}
</script>
<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .learn-more-btn:hover {
    color: white !important;
    background: $BCgovBlue5;
    opacity: .8;
  }

</style>
