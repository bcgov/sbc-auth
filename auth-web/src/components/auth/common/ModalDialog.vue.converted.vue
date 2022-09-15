import { defineComponent, toRefs, ref } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {
    title: { default: "", type: String },
    text: { default: "", type: String },
    showIcon: { default: true, type: Boolean },
    showActions: { default: true, type: Boolean },
    isPersistent: { default: false, type: Boolean },
    fullscreenOnMobile: { default: false, type: Boolean },
    isScrollable: { default: false, type: Boolean },
    dialogClass: { default: "", type: String },
    maxWidth: { default: "", type: String },
    showCloseIcon: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const {
      title,
      text,
      showIcon,
      showActions,
      isPersistent,
      fullscreenOnMobile,
      isScrollable,
      dialogClass,
      maxWidth,
      showCloseIcon,
    } = toRefs(props);
    const isOpen = ref(false);
    const open = () => {
      isOpen.value = true;
    };
    const close = () => {
      isOpen.value = false;
    };
    return { isOpen, open, close };
  },
});
