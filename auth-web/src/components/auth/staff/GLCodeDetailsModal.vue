<template>
  <v-row justify="center">
    <v-dialog
      v-model="isOpen"
      persistent
      max-width="900px"
    >
      <v-card class="pa-2">
        <v-card-title>
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
          <v-row class="mb-4">
            <v-col cols="12" sm="4">
              <div class="gl-code-label">Effective Dates</div>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                label="Start Date"
                v-model="glcodeDetails.startDate"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                label="End Date"
                v-model="glcodeDetails.endDate"
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row class="mb-10">
            <v-col cols="12" sm="4">
              <div class="gl-code-label">General Information</div>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                hide-details
                label="Client Number"
                v-model="glcodeDetails.client"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                hide-details
                label="Responsibility Center"
                v-model="glcodeDetails.responsibilityCentre"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4" offset-sm="4">
              <v-text-field
                filled
                hide-details
                label="Service Line"
                v-model="glcodeDetails.serviceLine"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                hide-details
                label="STOB(Standard Object of Expense)"
                v-model="glcodeDetails.stob"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4" offset-sm="4">
              <v-text-field
                filled
                hide-details
                label="Project Code"
                v-model="glcodeDetails.projectCode"
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row class="mb-10">
            <v-col cols="12" sm="4">
              <div class="gl-code-label">Service Fee Information</div>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                hide-details
                label="Client Number"
                v-model="glcodeDetails.serviceFeeClient"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                hide-details
                label="Responsibility Center"
                v-model="glcodeDetails.serviceFeeResponsibilityCentre"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4" offset-sm="4">
              <v-text-field
                filled
                hide-details
                label="Service Line"
                v-model="glcodeDetails.serviceFeeLine"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                filled
                hide-details
                label="STOB(Standard Object of Expense)"
                v-model="glcodeDetails.serviceFeeStob"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" sm="4" offset-sm="4">
              <v-text-field
                filled
                hide-details
                label="Project Code"
                v-model="glcodeDetails.serviceFeeProjectCode"
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row class="mb-10">
            <v-col cols="12" sm="4">
              <div class="gl-code-label">Associated Filing Types</div>
            </v-col>
            <v-col cols="12" sm="4">
              <ul>
                <li
                  v-for="filing in filingTypes"
                  :key="filing.feeScheduleId"
                >{{filing.corpType}}/{{filing.filingType}}</li>
              </ul>
            </v-col>
          </v-row>
          <v-divider></v-divider>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            depressed
            @click="save"
            width="90"
            class="font-weight-bold"
          >Save</v-btn>
          <v-btn
            depressed
            @click="close"
            width="90"
            class="font-weight-bold"
          >Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { FilingType, GLCode } from '@/models/Staff'
import StaffModule from '@/store/modules/staff'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

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
