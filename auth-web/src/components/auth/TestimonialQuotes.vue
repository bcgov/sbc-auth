<template>
  <section id="testimonials-container">
    <v-container class="quote-container">
      <div class="fading">
        <p>{{quotes[quoteIndex].text}}</p>
        <p><strong>&ndash; {{quotes[quoteIndex].author}}</strong></p>
      </div>
    </v-container>
  </section>
</template>
<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component({})
export default class TestimonialQuotes extends Vue {
  private quoteIndex = 0
  private quotes: Array<any> =
    [
      {
        text: 'We\'re incredibly excited to be able to incorporate as a Benefit Company in BC, it really reflects our values and the role we want to play.',
        author: 'BC Benefit Company user'
      },
      {
        text: 'This is a placeholder for a second quote.',
        author: 'BC Benefit Company user'
      },
      {
        text: 'This is a placeholder for third quote.',
        author: 'BC Benefit Company user'
      }
    ]

  mounted () {
    setInterval(() => {
      // Cycle quote index up or reset it once it reaches array size
      if (this.quoteIndex === this.quotes.length - 1) this.quoteIndex = 0
      else this.quoteIndex++
    }, 5000)
  }
}
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

    @keyframes fading {
      90% {
        opacity: 1;
      }
      100% {
        opacity: 0;
      }
      0% {
        opacity: 0;
      }
      10% {
        opacity: 1;
      }
    }

    .fading {
      animation: fading 5s ease-in-out infinite;
    }
  }

  #testimonials-container::after {
    border-color: transparent #003366 transparent transparent;
    border-image: none;
    border-style: solid;
    border-width: 20px;
    content: " ";
    display: block;
    top: -20px;
    float: right;
    position: relative;
  }
</style>
