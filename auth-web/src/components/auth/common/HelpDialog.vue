import { defineComponent, toRefs, ref } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
export default defineComponent({
  props: { helpDialogBlurb: { default: "", type: String } },
  setup(props, ctx) {
    const { helpDialogBlurb } = toRefs(props);
    const isDialogOpen = ref(false);
    const open = () => {
      isDialogOpen.value = true;
    };
    const close = () => {
      isDialogOpen.value = false;
    };
    return { isDialogOpen, open, close };
  },
});
