import { defineComponent, ref } from "@vue/composition-api";
import { Component, Emit, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const isDialogOpen = ref(false);
    const open = () => {
      isDialogOpen.value = true;
    };
    const close = () => {
      isDialogOpen.value = false;
    };
    const select = () => {
      close();
    };
    return { isDialogOpen, open, close, select };
  },
});
