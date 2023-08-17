<template>
  <div>
    <v-data-table
      class="glcodes-list"
      :headers="headerGLCodes"
      :items="glCodeList"
      :custom-sort="customSortActive"
      :no-data-text="$t('noGLCodeList')"
      :loading="isDataLoading"
    >
      <template #loading>
        Loading...
      </template>
      <template #[`item.updatedOn`]="{ item }">
        {{ formatDate(item.updatedOn) }}
      </template>
      <template #[`item.action`]="{ item }">
        <div class="btn-inline">
          <v-btn
            outlined
            color="primary"
            class="action-btn"
            :data-test="getIndexedTag('details-button', item.distributionCodeId)"
            @click="viewDetails(item)"
          >
            Details
          </v-btn>
        </div>
      </template>
    </v-data-table>
    <GLCodeDetailsModal
      ref="glcodeDetailsModal"
      @refresh-glcode-table="refreshTable"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { GLCode } from '@/models/Staff'
import GLCodeDetailsModal from '@/components/auth/staff/gl-code/GLCodeDetailsModal.vue'
import StaffModule from '@/store/modules/staff'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  components: {
    GLCodeDetailsModal
  },
  methods: {
    ...mapActions('staff', [
      'getGLCodeList'
    ])
  }
})
export default class GLCodesDataTable extends Vue {
  private staffStore = getModule(StaffModule, this.$store)
  @Prop({ default: '' }) private folioFilter: string
  private readonly getGLCodeList!: () => GLCode[]

  private glCodeList: GLCode[] = []
  private formatDate = CommonUtils.formatDisplayDate
  private isDataLoading = false

  private readonly headerGLCodes = [
    {
      text: 'Name',
      align: 'left',
      sortable: false,
      value: 'name'
    },
    {
      text: 'Client',
      align: 'left',
      sortable: false,
      value: 'client'
    },
    {
      text: 'Reponsiblity Center',
      align: 'left',
      sortable: false,
      value: 'responsibilityCentre'
    },
    {
      text: 'Service Line',
      align: 'left',
      sortable: false,
      value: 'serviceLine'
    },
    {
      text: 'STOB',
      align: 'left',
      value: 'stob',
      sortable: false
    },
    {
      text: 'Project Code',
      align: 'left',
      value: 'projectCode',
      sortable: false
    },
    {
      text: 'Modified',
      align: 'left',
      value: 'updatedOn',
      sortable: false
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '105'
    }
  ]

  $refs: {
    glcodeDetailsModal: GLCodeDetailsModal
  }

  private async loadGLCodeList () {
    this.isDataLoading = true
    this.glCodeList = await this.getGLCodeList()
    this.isDataLoading = false
  }

  async mounted () {
    await this.loadGLCodeList()
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private customSortActive (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    items.sort((a, b) => {
      return (isDesc) ? (a[index[0]] < b[index[0]] ? -1 : 1) : (b[index[0]] < a[index[0]] ? -1 : 1)
    })
    return items
  }

  private viewDetails (item) {
    this.$refs.glcodeDetailsModal.open(item)
  }

  private async refreshTable () {
    await this.loadGLCodeList()
  }
}
</script>

<style lang="scss" scoped>
::v-deep {
  table {
    table-layout: fixed;

    td {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }
  }
}

.action-btn {
  width: 5rem;
}
</style>
