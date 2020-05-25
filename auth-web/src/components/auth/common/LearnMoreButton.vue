<template>
  <v-btn large outlined color="#003366" class="btn-learn-more"
    href="https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/%7D"
    target="_blank" rel="noopener noreferrer">
    Learn More
  </v-btn>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component({})
export default class LearnMoreButton extends Vue {}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .btn-learn-more {
    margin-top: .5rem;
    font-weight: bold;
    width: 160px;
  }
</style>
