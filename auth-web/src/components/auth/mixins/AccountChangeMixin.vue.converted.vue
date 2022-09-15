import { defineComponent, ref, onBeforeUnmount } from "@vue/composition-api";
import Component from "vue-class-component";
import Vue from "vue";
export default defineComponent({
  name: "AccountChangeMixin",
  props: {},
  setup(_props, ctx) {
    const unregisterHandler = ref<() => void>(undefined);
    const setAccountChangedHandler = (handler: () => any) => {
      unregisterHandler.value = ctx.root.$store.subscribe((mutation, state) => {
        if (mutation.type === "org/setCurrentOrganization") {
          handler();
        }
      });
    };
    onBeforeUnmount(() => {
      unregisterHandler.value && unregisterHandler.value();
    });
    return { unregisterHandler, setAccountChangedHandler };
  },
});
