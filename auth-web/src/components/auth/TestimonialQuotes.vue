<template>
  <section id="testimonials-container">
    <v-container class="quote-container">
      <p>"We're incredibly excited to be able to incorporate as a Benefit Company in BC, it really reflects our values
        and the role we want to Play."</p>
      <p><strong>- BC Benefit Company user</strong></p>
    </v-container>
    <span class="arrow-down"></span>
  </section>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'

@Component({})
export default class TestimonialQuotes extends Vue {}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #testimonials-container {
    background: #E2E8EE;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;

    h2 {
      text-align: center;
    }

    .quote-container {
      padding: 1rem;
      color: #ffffff;
      background: #003366;
      font-size: 1.15rem;
      line-height: 2rem;
      text-align: center;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 150px;
      width: 50%;
    }
  }

  .arrow-down {
    margin-left: 48.3%;
    width: 0;
    height: 0;
    border-left: 32px solid transparent;
    border-right: 0px solid transparent;
    border-top: 36px solid #003366;
  }
</style>
