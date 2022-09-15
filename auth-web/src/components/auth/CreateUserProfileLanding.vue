import { defineComponent, toRefs, ref, onMounted } from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import CreateUserProfileForm from "@/components/auth/CreateUserProfileForm.vue";
import InterimLanding from "@/components/auth/common/InterimLanding.vue";
import Vue from "vue";
export default defineComponent({
  components: {
    CreateUserProfileForm,
    InterimLanding,
  },
  props: { token: { type: String }, orgName: { default: "", type: String } },
  setup(props, ctx) {
    const { token, orgName } = toRefs(props);
    const isLoading = ref(true);
    const inviteError = ref(false);
    const showErrorOccured = () => {
      inviteError.value = true;
    };
    onMounted(async () => {
      isLoading.value = false;
    });
    return { isLoading, inviteError, showErrorOccured };
  },
});
