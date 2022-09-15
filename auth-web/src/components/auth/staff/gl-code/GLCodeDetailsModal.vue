import { defineComponent, ref, computed } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { FilingType, GLCode } from "@/models/Staff";
import { mapActions, mapState } from "vuex";
import StaffModule from "@/store/modules/staff";
import { getModule } from "vuex-module-decorators";
import moment from "moment";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const getGLCodeFiling = () =>
      ctx.root.$store.dispatch("staff/getGLCodeFiling");
    const updateGLCodeFiling = () =>
      ctx.root.$store.dispatch("staff/updateGLCodeFiling");
    const getGLCode = () => ctx.root.$store.dispatch("staff/getGLCode");
    const staffStore = ref(getModule(StaffModule, ctx.root.$store));
    const getGLCodeFiling =
      ref<(distributionCodeId: number) => FilingType[]>(undefined);
    const updateGLCodeFiling =
      ref<(glcodeFilingData: GLCode) => any>(undefined);
    const getGLCode = ref<(distributionCodeId: number) => GLCode>(undefined);
    const isOpen = ref(false);
    const glcodeDetails = ref<GLCode>({} as GLCode);
    const filingTypes = ref<FilingType[]>([]);
    const tab = ref(null);
    const startDatePicker = ref<boolean>(false);
    const endDatePicker = ref<boolean>(false);
    const filingTypeHeaders = ref([
      {
        text: "Corporation Type",
        align: "left",
        sortable: false,
        value: "corpType",
      },
      {
        text: "Filing Type",
        align: "left",
        sortable: false,
        value: "filingType",
      },
    ]);
    const startDateFormatted = computed(() => {
      return glcodeDetails.value?.startDate
        ? moment(glcodeDetails.value.startDate).format("MM-DD-YYYY")
        : "";
    });
    const endDateFormatted = computed(() => {
      return glcodeDetails.value?.endDate
        ? moment(glcodeDetails.value.endDate).format("MM-DD-YYYY")
        : "";
    });
    const open = async (selectedData: GLCode) => {
      if (selectedData?.distributionCodeId) {
        if (selectedData?.serviceFeeDistributionCodeId) {
          selectedData.serviceFee = await getGLCode.value(
            selectedData?.serviceFeeDistributionCodeId
          );
        }
        filingTypes.value = await getGLCodeFiling.value(
          selectedData.distributionCodeId
        );
        glcodeDetails.value = { ...selectedData };
        isOpen.value = true;
      } else {
        console.error("distributionCodeId not found!");
      }
    };
    const close = () => {
      glcodeDetails.value = {} as GLCode;
      filingTypes.value = [];
      isOpen.value = false;
    };
    const save = async () => {
      for (const key in glcodeDetails.value) {
        if (glcodeDetails.value[key] === null) {
          delete glcodeDetails.value[key];
        }
      }
      const updated = await updateGLCodeFiling.value(glcodeDetails.value);
      if (updated.distributionCodeId) {
        close();
        refreshGLCodeTable();
      }
    };
    const refreshGLCodeTable = () => {};
    return {
      getGLCodeFiling,
      updateGLCodeFiling,
      getGLCode,
      staffStore,
      getGLCodeFiling,
      updateGLCodeFiling,
      getGLCode,
      isOpen,
      glcodeDetails,
      filingTypes,
      tab,
      startDatePicker,
      endDatePicker,
      filingTypeHeaders,
      startDateFormatted,
      endDateFormatted,
      open,
      close,
      save,
      refreshGLCodeTable,
    };
  },
});
