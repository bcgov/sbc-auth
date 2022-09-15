import { defineComponent, computed, ref } from "@vue/composition-api";
import { Component, Emit, Vue } from "vue-property-decorator";
import CommonUtils from "@/util/common-util";
import { Invitation } from "@/models/Invitation";
import { mapState } from "vuex";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const pendingOrgInvitations = computed(
      () => ctx.root.$store.state.org.pendingOrgInvitations
    );
    const pendingOrgInvitations = ref<Invitation[]>(undefined);
    const headerInvitations = ref([
      {
        text: "Email",
        align: "left",
        sortable: true,
        value: "recipientEmail",
      },
      {
        text: "Invitation Sent",
        align: "left",
        sortable: true,
        value: "sentDate",
      },
      {
        text: "Expires",
        align: "left",
        sortable: true,
        value: "expiresOn",
      },
      {
        text: "Actions",
        align: "right",
        value: "action",
        sortable: false,
      },
    ]);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const indexedInvitations = computed(() => {
      return pendingOrgInvitations.value.map((item, index) => ({
        index,
        ...item,
      }));
    });
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const confirmRemoveInvite = (invititation: Invitation) => {};
    const resend = (invitation: Invitation) => {};
    return {
      pendingOrgInvitations,
      pendingOrgInvitations,
      headerInvitations,
      formatDate,
      indexedInvitations,
      getIndexedTag,
      confirmRemoveInvite,
      resend,
    };
  },
});
