import { defineComponent, computed, toRefs, ref } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import { Member } from "@/models/Organization";
import moment from "moment";
export default defineComponent({
  props: { userNamefilterText: { default: "", type: String } },
  setup(props, ctx) {
    const pendingOrgMembers = computed(
      () => ctx.root.$store.state.org.pendingOrgMembers
    );
    const { userNamefilterText } = toRefs(props);
    const pendingOrgMembers = ref<Member[]>(undefined);
    const headerPendingMembers = ref([
      {
        text: "Team Member",
        align: "left",
        sortable: true,
        value: "name",
      },
      {
        text: "Actions",
        align: "right",
        value: "action",
        sortable: false,
      },
    ]);
    const indexedPendingMembers = computed(() => {
      let pendingMembers = [];
      if (userNamefilterText.value) {
        pendingMembers = pendingOrgMembers.value.filter((element) => {
          const username = `${element.user?.firstname || ""} ${
            element.user?.lastname || ""
          }`.trim();
          const found = username.match(
            new RegExp(userNamefilterText.value, "i")
          );
          if (found?.length) {
            return element;
          }
        });
        filteredMembersCount(pendingMembers.length);
      } else {
        pendingMembers = pendingOrgMembers.value;
      }
      return pendingMembers.map((item, index) => ({
        index,
        ...item,
      }));
    });
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const filteredMembersCount = (count: number) => {
      return count;
    };
    const customSortPending = (items, index, isDescending) => {
      const isDesc = isDescending.length > 0 && isDescending[0];
      items.sort((a, b) => {
        if (isDesc) {
          return a.user.firstname < b.user.firstname ? -1 : 1;
        } else {
          return b.user.firstname < a.user.firstname ? -1 : 1;
        }
      });
      return items;
    };
    const confirmApproveMember = (member: Member) => {};
    const confirmDenyMember = (member: Member) => {};
    return {
      pendingOrgMembers,
      pendingOrgMembers,
      headerPendingMembers,
      indexedPendingMembers,
      getIndexedTag,
      filteredMembersCount,
      customSortPending,
      confirmApproveMember,
      confirmDenyMember,
    };
  },
});
