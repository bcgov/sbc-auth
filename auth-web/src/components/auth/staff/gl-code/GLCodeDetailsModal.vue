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
        <v-tabs
          v-model="tab"
          class="mb-7"
        >
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
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-menu
                      v-model="startDatePicker"
                      :close-on-content-click="false"
                      transition="scale-transition"
                      offset-y
                      max-width="290px"
                      min-width="290px"
                    >
                      <template #activator="{ on, attrs }">
                        <v-text-field
                          v-model="startDateFormatted"
                          label="Start Date"
                          filled
                          hide-details
                          readonly
                          v-bind="attrs"
                          v-on="on"
                        />
                      </template>
                      <v-date-picker
                        v-model="glcodeDetails.startDate"
                        no-title
                        @input="startDatePicker = false"
                      />
                    </v-menu>
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-menu
                      v-model="endDatePicker"
                      :close-on-content-click="false"
                      transition="scale-transition"
                      offset-y
                      max-width="290px"
                      min-width="290px"
                    >
                      <template #activator="{ on, attrs }">
                        <v-text-field
                          v-model="endDateFormatted"
                          label="End Date"
                          filled
                          hide-details
                          readonly
                          v-bind="attrs"
                          v-on="on"
                        />
                      </template>
                      <v-date-picker
                        v-model="glcodeDetails.endDate"
                        no-title
                        @input="endDatePicker = false"
                      />
                    </v-menu>
                  </v-col>
                </v-row>
              </fieldset>

              <!-- General Information -->
              <fieldset class="mt-6">
                <legend>General Information</legend>
                <v-row>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.client"
                      filled
                      hide-details
                      label="Client Number"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.responsibilityCentre"
                      filled
                      hide-details
                      label="Responsibility Center"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.serviceLine"
                      filled
                      hide-details
                      label="Service Line"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.stob"
                      filled
                      hide-details
                      label="STOB (Standard Object of Expense)"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.projectCode"
                      filled
                      hide-details
                      label="Project Code"
                    />
                  </v-col>
                </v-row>
              </fieldset>

              <!-- Service Fee Information -->
              <fieldset
                v-if="glcodeDetails.serviceFee"
                class="mt-6"
              >
                <legend>
                  Service Fee Information
                </legend>
                <v-row>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.serviceFee.client"
                      filled
                      hide-details
                      label="Client Number"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.serviceFee.responsibilityCentre"
                      filled
                      hide-details
                      label="Responsibility Center"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.serviceFee.serviceLine"
                      filled
                      hide-details
                      label="Service Line"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.serviceFee.stob"
                      filled
                      hide-details
                      label="STOB (Standard Object of Expense)"
                    />
                  </v-col>
                  <v-col
                    cols="12"
                    sm="6"
                    class="col"
                  >
                    <v-text-field
                      v-model="glcodeDetails.serviceFee.projectCode"
                      filled
                      hide-details
                      label="Project Code"
                    />
                  </v-col>
                </v-row>
              </fieldset>
            </div>

            <v-divider class="mt-6 mb-8" />

            <div class="d-flex">
              <v-spacer />
              <v-btn
                large
                color="primary"
                class="font-weight-bold mr-2"
                width="100"
                @click="save"
              >
                Save
              </v-btn>
              <v-btn
                large
                depressed
                width="100"
                @click="close"
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
            />
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { FilingType, GLCode } from '@/models/Staff'
import StaffModule from '@/store/modules/staff'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'
import moment from 'moment'

@Component({
  methods: {
    ...mapActions('staff', [
      'getGLCodeFiling',
      'updateGLCodeFiling',
      'getGLCode'
    ])
  }
})
export default class GLCodeDetailsModal extends Vue {
  private staffStore = getModule(StaffModule, this.$store)
  private readonly getGLCodeFiling!: (distributionCodeId: number) => FilingType[]
  private readonly updateGLCodeFiling!: (glcodeFilingData: GLCode) => any
  private readonly getGLCode!: (distributionCodeId: number) => GLCode
  private isOpen = false
  private glcodeDetails: GLCode = {} as GLCode
  private filingTypes: FilingType[] = []
  private tab = null
  private startDatePicker: boolean = false
  private endDatePicker: boolean = false

  public async open (selectedData: GLCode) {
    if (selectedData?.distributionCodeId) {
      if (selectedData?.serviceFeeDistributionCodeId) {
        selectedData.serviceFee = await this.getGLCode(selectedData?.serviceFeeDistributionCodeId)
      }
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

  private get startDateFormatted () {
    return this.glcodeDetails?.startDate ? moment(this.glcodeDetails.startDate).format('MM-DD-YYYY') : ''
  }

  private get endDateFormatted () {
    return this.glcodeDetails?.endDate ? moment(this.glcodeDetails.endDate).format('MM-DD-YYYY') : ''
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
