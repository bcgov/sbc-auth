import { defineComponent, toRefs, ref, onMounted } from "@vue/composition-api";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { GLCode } from "@/models/Staff";
import GLCodeDetailsModal from "@/components/auth/staff/gl-code/GLCodeDetailsModal.vue";
import StaffModule from "@/store/modules/staff";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    GLCodeDetailsModal,
  },
  props: { folioFilter: { default: "", type: String } },
  setup(props, ctx) {
    const getGLCodeList = () => ctx.root.$store.dispatch("staff/getGLCodeList");
    const { folioFilter } = toRefs(props);
    const staffStore = ref(getModule(StaffModule, ctx.root.$store));
    const getGLCodeList = ref<() => GLCode[]>(undefined);
    const glCodeList = ref<GLCode[]>([]);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const isDataLoading = ref(false);
    const headerGLCodes = ref([
      {
        text: "Name",
        align: "left",
        sortable: false,
        value: "name",
      },
      {
        text: "Client",
        align: "left",
        sortable: false,
        value: "client",
      },
      {
        text: "Reponsiblity Center",
        align: "left",
        sortable: false,
        value: "responsibilityCentre",
      },
      {
        text: "Service Line",
        align: "left",
        sortable: false,
        value: "serviceLine",
      },
      {
        text: "STOB",
        align: "left",
        value: "stob",
        sortable: false,
      },
      {
        text: "Project Code",
        align: "left",
        value: "projectCode",
        sortable: false,
      },
      {
        text: "Modified",
        align: "left",
        value: "updatedOn",
        sortable: false,
      },
      {
        text: "Actions",
        align: "left",
        value: "action",
        sortable: false,
        width: "105",
      },
    ]);
    const $refs = ref<{
      glcodeDetailsModal: GLCodeDetailsModal;
    }>(undefined);
    const loadGLCodeList = async () => {
      isDataLoading.value = true;
      glCodeList.value = await getGLCodeList.value();
      isDataLoading.value = false;
    };
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const customSortActive = (items, index, isDescending) => {
      const isDesc = isDescending.length > 0 && isDescending[0];
      items.sort((a, b) => {
        return isDesc
          ? a[index[0]] < b[index[0]]
            ? -1
            : 1
          : b[index[0]] < a[index[0]]
          ? -1
          : 1;
      });
      return items;
    };
    const viewDetails = (item) => {
      ctx.refs.glcodeDetailsModal.open(item);
    };
    const refreshTable = async () => {
      await loadGLCodeList();
    };
    onMounted(async () => {
      await loadGLCodeList();
    });
    return {
      getGLCodeList,
      staffStore,
      getGLCodeList,
      glCodeList,
      formatDate,
      isDataLoading,
      headerGLCodes,
      $refs,
      loadGLCodeList,
      getIndexedTag,
      customSortActive,
      viewDetails,
      refreshTable,
    };
  },
});
