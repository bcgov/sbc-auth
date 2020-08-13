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
      <template v-slot:loading>
        Loading...
      </template>
      <template v-slot:item.updatedOn="{ item }">
        {{formatDate(item.updatedOn)}}
      </template>
      <template v-slot:item.action="{ item }">
        <div class="btn-inline">
          <v-btn
            outlined
            small
            color="primary"
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
    >
    </GLCodeDetailsModal>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import { GLCode } from '@/models/Staff'
import GLCodeDetailsModal from '@/components/auth/staff/GLCodeDetailsModal.vue'
import StaffModule from '@/store/modules/staff'
import { getModule } from 'vuex-module-decorators'

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
  private readonly getGLCodeList!: (filterParams: any) => GLCode[]

  private glCodeList: GLCode[] = [];
  private formatDate = CommonUtils.formatDisplayDate
  private isDataLoading = false

  private readonly headerGLCodes = [
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
      align: 'right',
      value: 'projectCode',
      sortable: false
    },
    {
      text: 'Modified',
      align: 'right',
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

  private async loadGLCodeList (pageNumber?: number, itemsPerPage?: number) {
    this.isDataLoading = true
    const filterParams = {
      filterPayload: {
        dateFilter: null,
        folioNumber: this.folioFilter
      },
      pageNumber: pageNumber,
      pageLimit: itemsPerPage
    }
    this.glCodeList = await this.getGLCodeList(filterParams)
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
}
</script>

<style lang="scss" scoped>
.v-list--dense {
  .v-list-item {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }

  .v-list-item .v-list-item__title {
    margin-bottom: 0.25rem;
    font-weight: 700;
  }
}

.status-tooltip-icon {
  margin-top: -4px;
  margin-right: 5px;
  margin-left: 2px;
}

.v-tooltip__content:before {
  content: ' ';
  position: absolute;
  top: -20px;
  left: 50%;
  margin-left: -10px;
  width: 20px;
  height: 20px;
  border-width: 10px 10px 10px 10px;
  border-style: solid;
  border-color: transparent transparent var(--v-grey-darken4) transparent;
}

::v-deep {
  td {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    height: auto;
    vertical-align: top;
    overflow: hidden;
  }

  .glcodes-list {
    .v-data-table-header {
      margin-bottom: -2px;
    }

    .product-name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

thead + thead {
  position: absolute;
  top: -2px;
}
</style>
