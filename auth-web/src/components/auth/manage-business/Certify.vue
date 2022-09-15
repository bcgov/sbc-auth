import { defineComponent, toRefs, ref, computed } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import { namespace } from "vuex-class";
const UserModule = namespace("user");
export default defineComponent({
  props: {
    entity: { default: "business", type: String },
    clause: { default: "", type: String },
  },
  setup(props, ctx) {
    const { entity, clause } = toRefs(props);
    const isCertified = ref(false);
    const currentUserName = computed((): string => {
      return `${currentUser.lastName}, ${currentUser.firstName}`;
    });
    const emitIsCertified = (isCertified: boolean): void => {};
    return { isCertified, currentUserName, emitIsCertified };
  },
});
