<template>
  <section id="testimonials-container">
    <v-container class="quote-container">
      <div>
        <p class="quote-text">{{quotes[quoteIndex].text}}</p>
        <p class="quote-author">&ndash; {{quotes[quoteIndex].author}}</p>
      </div>
    </v-container>
  </section>
</template>
<script lang="ts">
// import { Component, Vue } from 'vue-property-decorator'
import { defineComponent, onMounted, ref } from '@vue/composition-api'
import vue from 'vue'

export default defineComponent({
  name: 'TestimonialQuotes',
  setup () {
    const quoteIndex = ref(0)
    const quotes = [
      {
        text: 'We are really excited by the idea of incorporating as a Benefit Company, it really makes sense for us and the way we want to run our business.',
        author: 'Business Founder'
      }
    ] as { text: string, author: string}[]

    const setInterval = () => {
      // Cycle quote index up or reset it once it reaches array size
      if (quoteIndex.value === quotes.length - 1) quoteIndex.value = 0
      else quoteIndex.value++
    }

    onMounted(setInterval)
    return {
      quoteIndex,
      quotes
    }
  }
})

// @Component({})
// export default class TestimonialQuotes extends Vue {
//   private quoteIndex = 0
//   private quotes: Array<any> =
//     [
//       {
//         text: 'We are really excited by the idea of incorporating as a Benefit Company, it really makes sense for us and the way we want to run our business.',
//         author: 'Business Founder'
//       }
//     ]

//   mounted () {
//     setInterval(() => {
//       // Cycle quote index up or reset it once it reaches array size
//       if (this.quoteIndex === this.quotes.length - 1) this.quoteIndex = 0
//       else this.quoteIndex++
//     }, 5000)
//   }
// }
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #testimonials-container {
    background: #E2E8EE;
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;

    h2 {
      text-align: center;
    }

    .quote-container {
      padding: 2rem .5rem 0 .5rem;
      color: white;
      background: $BCgovBlue5;
      font-size: 1.15rem;
      line-height: 2rem;
      text-align: center;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      min-height: 150px;
      width: 60%;
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

    .quote-text {
      max-width: 45rem;
      color: #FFFFFF;
      font-size: 1.125rem;
      letter-spacing: 0;
      line-height: 1.5rem;
      text-align: center;
    }

    .quote-author {
      font-size: .875rem;
      font-weight: bold;
    }
  }

  #testimonials-container::after {
    border-color: transparent $BCgovBlue5 transparent transparent;
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
