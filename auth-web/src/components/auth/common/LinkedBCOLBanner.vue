import {
  defineComponent,
  toRefs,
  ref,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { BcolAccountDetails, BcolProfile } from "@/models/bcol";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import BcolLogin from "@/components/auth/create-account/BcolLogin.vue";
export default defineComponent({
  components: {
    BcolLogin,
  },
  props: {
    showUnlinkAccountBtn: { default: false, type: Boolean },
    showEditBtn: { default: false, type: Boolean },
    forceEditMode: { default: false, type: Boolean },
    bcolAccountName: { default: "", type: String },
    bcolAccountDetails: {
      default: () => ({} as BcolAccountDetails),
      type: Object as PropType<BcolAccountDetails>,
    },
  },
  setup(props, ctx) {
    const {
      showUnlinkAccountBtn,
      showEditBtn,
      forceEditMode,
      bcolAccountName,
      bcolAccountDetails,
    } = toRefs(props);
    const editMode = ref<boolean>(false);
    const unlinkAccount = () => {};
    const emitBcolInfo = (bcolProfile: BcolProfile) => {
      return bcolProfile;
    };
    const editAccount = () => {
      editMode.value = true;
    };
    onMounted(async () => {
      editMode.value = forceEditMode.value || false;
      emitBcolInfo({});
    });
    return { editMode, unlinkAccount, emitBcolInfo, editAccount };
  },
});
