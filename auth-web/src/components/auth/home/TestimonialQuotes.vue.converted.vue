import { defineComponent, ref, onMounted } from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const quoteIndex = ref(0);
    const quotes = ref<Array<any>>([
      {
        text: "We are really excited by the idea of incorporating as a Benefit Company, it really makes sense for us and the way we want to run our business.",
        author: "Business Founder",
      },
    ]);
    onMounted(() => {
      setInterval(() => {
        if (quoteIndex.value === quotes.value.length - 1) quoteIndex.value = 0;
        else quoteIndex.value++;
      }, 5000);
    });
    return { quoteIndex, quotes };
  },
});
