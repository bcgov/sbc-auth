<template>
  <v-btn large outlined color="bcgovblue" class="font-weight-bold"
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
