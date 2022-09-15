import { defineComponent, computed, ref } from "@vue/composition-api";
import { Component, Mixins } from "vue-property-decorator";
import { mapActions, mapMutations, mapState } from "vuex";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import AccountLoginOptionPicker from "@/components/auth/common/AccountLoginOptionPicker.vue";
import { LoginSource } from "@/util/constants";
export default defineComponent({
  components: {
    AccountLoginOptionPicker,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const memberLoginOption = computed(
      () => ctx.root.$store.state.org.memberLoginOption
    );
    const updateLoginOption = () =>
      ctx.root.$store.dispatch("org/updateLoginOption");
    const isBtnSaved = ref(false);
    const disableSaveBtn = ref(true);
    const updateLoginOption =
      ref<(loginType: string) => Promise<string>>(undefined);
    const authType = ref(LoginSource.BCSC.toString());
    const errorMessage = ref<string>("");
    const setLoginOption = (loginType: string) => {
      authType.value = loginType;
      disableSaveBtn.value = false;
      isBtnSaved.value = false;
      window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth",
      });
    };
    const submit = async () => {
      isBtnSaved.value = false;
      try {
        await updateLoginOption.value(authType.value);
        isBtnSaved.value = true;
      } catch (err) {
        isBtnSaved.value = false;
        disableSaveBtn.value = false;
        console.error("Error", err);
      }
    };
    return {
      currentOrganization,
      memberLoginOption,
      updateLoginOption,
      isBtnSaved,
      disableSaveBtn,
      updateLoginOption,
      authType,
      errorMessage,
      setLoginOption,
      submit,
    };
  },
});
