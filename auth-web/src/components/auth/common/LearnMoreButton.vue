<template>
  <v-btn large outlined color="#003366" class="btn-learn-more"
    :href="redirectUrl"
    target="_blank" rel="noopener noreferrer">
    <span class="btn-text">Learn More</span>
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

  .btn-learn-more:hover {
    background-color: $BCgovBlue5;
    opacity: .8;

    .btn-text {
      color: #ffffff;
    }
  }
</style>
