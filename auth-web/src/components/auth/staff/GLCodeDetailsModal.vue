<template>
  <v-dialog
    v-model="isOpen"
    persistent
    max-width="900px"
  >
    <v-card>
      <v-card-title class="pb-4">
        <h3>General Ledger Code Details</h3>
        <v-btn
          large
          icon
          @click="close"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>

        <v-tabs v-model="tab" class="mb-7">
          <v-tab>Details</v-tab>
          <v-tab>Associated Filing Types</v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab">
          <v-tab-item>

            <div class="pt-4">

            <!-- Effective Dates -->
            <fieldset>
              <legend>Effective Dates</legend>
              <v-row>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Start Date"
                    v-model="glcodeDetails.startDate"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="End Date"
                    v-model="glcodeDetails.endDate"
                  >
                  </v-text-field>
                </v-col>
              </v-row>
            </fieldset>

            <!-- General Information -->
            <fieldset class="mt-6">
              <legend>General Information</legend>
              <v-row>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Client Number"
                    v-model="glcodeDetails.client"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Responsibility Center"
                    v-model="glcodeDetails.responsibilityCentre"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Service Line"
                    v-model="glcodeDetails.serviceLine"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="STOB (Standard Object of Expense)"
                    v-model="glcodeDetails.stob"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Project Code"
                    v-model="glcodeDetails.projectCode"
                  >
                  </v-text-field>
                </v-col>
              </v-row>
            </fieldset>

            <!-- Service Fee Information -->
            <fieldset class="mt-6">
              <legend>
                Service Fee Information
              </legend>
              <v-row>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Client Number"
                    v-model="glcodeDetails.serviceFeeClient"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Responsibility Center"
                    v-model="glcodeDetails.serviceFeeResponsibilityCentre"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Service Line"
                    v-model="glcodeDetails.serviceFeeLine"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="STOB (Standard Object of Expense)"
                    v-model="glcodeDetails.serviceFeeStob"
                  >
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="6" class="col">
                  <v-text-field
                    filled
                    hide-details
                    label="Project Code"
                    v-model="glcodeDetails.serviceFeeProjectCode"
                  >
                  </v-text-field>
                </v-col>
              </v-row>
            </fieldset>

            </div>

            <v-divider class="mt-6 mb-8"></v-divider>

            <div class="d-flex">
              <v-spacer></v-spacer>
              <v-btn
                large
                color="primary"
                class="font-weight-bold mr-2"
                @click="save"
                width="100"
              >
                Save
              </v-btn>
              <v-btn
                large
                depressed
                @click="close"
                width="100"
              >
                Cancel
              </v-btn>
            </div>

          </v-tab-item>
          <v-tab-item>
            <v-data-table
              :headers="filingTypeHeaders"
              :items="filingTypes"
              item-key="feeScheduleId"
              hide-default-footer
            >
            </v-data-table>
          </v-tab-item>
        </v-tabs-items>

      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { FilingType, GLCode } from '@/models/Staff'
import { mapActions, mapState } from 'vuex'
import StaffModule from '@/store/modules/staff'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapActions('staff', [
      'getGLCodeFiling',
      'updateGLCodeFiling'
    ])
  }
})
export default class GLCodeDetailsModal extends Vue {
  private staffStore = getModule(StaffModule, this.$store)
  private readonly getGLCodeFiling!: (distributionCodeId: string) => FilingType[]
  private readonly updateGLCodeFiling!: (glcodeFilingData: GLCode) => any
  private isOpen = false
  private glcodeDetails: GLCode = {} as GLCode
  private filingTypes: FilingType[] = []
  private tab = null

  public async open (selectedData) {
    if (selectedData?.distributionCodeId) {
      this.filingTypes = await this.getGLCodeFiling(selectedData.distributionCodeId)
      this.glcodeDetails = { ...selectedData }
      this.isOpen = true
    } else {
      // eslint-disable-next-line no-console
      console.error('distributionCodeId not found!')
    }
  }

  private readonly filingTypeHeaders = [
    {
      text: 'Corporation Type',
      align: 'left',
      sortable: false,
      value: 'corpType'
    },
    {
      text: 'Filing Type',
      align: 'left',
      sortable: false,
      value: 'filingType'
    }
  ]

  public close () {
    this.glcodeDetails = {} as GLCode
    this.filingTypes = []
    this.isOpen = false
  }

  private async save () {
    // removing null key-values to aviod error from backend
    for (const key in this.glcodeDetails) {
      if (this.glcodeDetails[key] === null) {
        delete this.glcodeDetails[key]
      }
    }
    const updated = await this.updateGLCodeFiling(this.glcodeDetails)
    if (updated.distributionCodeId) {
      this.close()
      this.refreshGLCodeTable()
    }
  }

  @Emit('refresh-glcode-table')
  refreshGLCodeTable () {
  }
}
</script>

<style lang="scss" scoped>
.gl-code-label {
  color: black
}
</style>
