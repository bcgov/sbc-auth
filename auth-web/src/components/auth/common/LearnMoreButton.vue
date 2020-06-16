<template>
  <v-btn large outlined color="#003366" class="btn-learn-more"
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
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .btn-learn-more {
    margin-top: .5rem;
    font-weight: bold;
    width: 160px;
  }
</style>
