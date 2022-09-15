import { defineComponent, computed, toRefs, ref } from "@vue/composition-api";
import {
  AddUserBody,
  BulkUsersFailed,
  BulkUsersSuccess,
} from "@/models/Organization";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { IdpHint, Pages } from "@/util/constants";
import { mapActions, mapMutations, mapState } from "vuex";
import ConfigHelper from "@/util/config-helper";
import OrgModule from "@/store/modules/org";
import { User } from "@/models/user";
export default defineComponent({
  filters: {
    filterLoginSource(value: string) {
      return value.replace("bcros/", "");
    },
  },
  props: { action: { type: String } },
  setup(props, ctx) {
    const createdUsers = computed(() => ctx.root.$store.state.org.createdUsers);
    const failedUsers = computed(() => ctx.root.$store.state.org.failedUsers);
    const { action } = toRefs(props);
    const createdUsers = ref<BulkUsersSuccess[]>(undefined);
    const failedUsers = ref<BulkUsersFailed[]>(undefined);
    const loginUrl = ref<string>(ConfigHelper.getDirectorSearchURL());
    const close = () => {};
    return {
      createdUsers,
      failedUsers,
      createdUsers,
      failedUsers,
      loginUrl,
      close,
    };
  },
});
