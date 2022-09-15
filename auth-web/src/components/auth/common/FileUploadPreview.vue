import {
  defineComponent,
  toRefs,
  ref,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop } from "vue-property-decorator";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import Vue from "vue";
import { mapActions } from "vuex";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {
    inputFile: { type: Object as PropType<File> },
    isRequired: { default: true, type: Boolean },
    maxSize: { default: 0, type: Number },
  },
  setup(props, ctx) {
    const resetAccountSetupProgress = () =>
      ctx.root.$store.dispatch("org/resetAccountSetupProgress");
    const { inputFile, isRequired, maxSize } = toRefs(props);
    const fileUpload = ref(null);
    const $refs = ref<{
      fileUploadInput: HTMLFormElement;
    }>(undefined);
    const fileUploadRules = ref([
      (v) => {
        if (isRequired.value) {
          return !!v || "Affidavit file is required";
        }
        return true;
      },
      (file) => {
        if (maxSize.value) {
          return (
            file?.size <= maxSize.value * 1000 ||
            "File size exceed max allowed size"
          );
        }
        return true;
      },
    ]);
    const fileChange = (file) => {
      emitFileSelected(file);
    };
    const emitFileSelected = (file) => {
      isFileValid();
      return file;
    };
    const isFileValid = () => {
      return ctx.refs.fileUploadInput.validate();
    };
    onMounted(() => {
      if (inputFile.value) {
        fileUpload.value = inputFile.value;
        ctx.root.$nextTick(() => {
          isFileValid();
        });
      }
    });
    return {
      resetAccountSetupProgress,
      fileUpload,
      $refs,
      fileUploadRules,
      fileChange,
      emitFileSelected,
      isFileValid,
    };
  },
});
