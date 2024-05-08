<template>
  <section id="dissolution-schedule">
    <article class="section-container px-6 py-8">
      <!-- Dissolution Batch Size -->
      <template v-if="isEdit">
        <v-row no-gutters>
          <v-col
            cols="12"
            sm="3"
          >
            <label id="company-label">Dissolution Batch Size</label>
          </v-col>
          <v-col
            cols="12"
            sm="9"
          >
            <v-text-field
              ref="numberOfBusinessesRef"
              v-model="numberOfBusinesses"
              filled
              type="number"
              label="Dissolution Batch Size"
              hint="The number of businesses to be moved into D1 dissolution per batch. Maximum of 600."
              :rules="dissolutionBatchSizeRules"
              req
              persistent-hint
            />
          </v-col>
        </v-row>

        <v-divider class="mb-8 mt-6" />
      </template>

      <!-- Schedule Summary -->
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
        >
          <label id="company-label">Schedule Summary</label>
        </v-col>
        <v-col
          cols="12"
          sm="6"
        >
          <span>
            Moving <strong>{{ scheduleSummaryNumber }}</strong> businesses into D1 dissolution every
            <strong>Tuesday, Wednesday, and Thursday</strong> at <strong>12:15 a.m.</strong> Pacific Time.
          </span>
        </v-col>

        <template v-if="!isEdit">
          <v-col
            cols="6"
            sm="3"
            class="text-right"
          >
            <v-btn
              color="primary"
              class="action-btn px-6"
              @click="actionBtnClicked()"
            >
              {{ actionBtnText }}
            </v-btn>
            <span>
              <v-menu
                v-model="menu"
                offset-y
                nudge-left="90"
              >
                <template #activator="{ on }">
                  <v-btn
                    color="primary"
                    class="more-actions-btn menu-btn px-3"
                    v-on="on"
                  >
                    <v-icon v-if="menu">
                      mdi-menu-up
                    </v-icon>
                    <v-icon v-else>
                      mdi-menu-down
                    </v-icon>
                  </v-btn>
                </template>

                <v-list dense>
                  <v-list-item @click="triggerEditOnOff()">
                    <v-list-item-subtitle>
                      <v-icon>mdi-pencil</v-icon>
                      <span class="pl-2 edit-txt">Edit</span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-menu>
            </span>
          </v-col>
        </template>
      </v-row>

      <!-- Cancel/Save buttons -->
      <template v-if="isEdit">
        <v-divider class="mb-8 mt-8" />
        <v-row no-gutters>
          <v-col
            cols="12"
            class="text-right"
          >
            <v-btn
              color="primary"
              large
              outlined
              class="mr-3"
              @click="triggerEditOnOff()"
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              large
              @click="saveBtnClicked()"
            >
              Save
            </v-btn>
          </v-col>
        </v-row>
      </template>
    </article>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useStaffStore } from '@/stores/staff'

export default defineComponent({
  name: 'DissolutionSchedule',
  emits: ['update:onHold'],
  setup (_, { emit }) {
    const state = reactive({
      menu: false,
      numberOfBusinesses: 0,
      numberOfBusinessesRef: null,
      isEdit: false,
      isOnHold: false
    })
    const staffStore = useStaffStore()

    /**
     * Set local properties to values from the store.
     * TODO: Update once BE work is done.
     */
    onMounted(() => {
      state.numberOfBusinesses = staffStore.getDissolutionBatchSize()
      state.isOnHold = staffStore.isDissolutionBatchOnHold()
    })

    /**
     * Update whether the dissolution batch is paused or running.
     * Emit the status to the parent to know whether the "Paused" badge is going to be shown.
     * TODO: Modify/Update this once the BE is done.
     */
    const actionBtnClicked = (): void => {
      state.isOnHold = !staffStore.isDissolutionBatchOnHold()
      // Emit whether on hold or not to the parent.
      emit('update:onHold', state.isOnHold)
      staffStore.updateDissolutionBatchOnHold(!staffStore.isDissolutionBatchOnHold())
    }

    /** Edit, Cancel, or Save (successful) button is clicked. */
    const triggerEditOnOff = (): void => {
      state.isEdit = !state.isEdit
      // closing the menu
      state.menu = false
    }

    /**
     * Save button is clicked. Update the dissolution batch size.
     * Only save if the inputted number is valid.
     * TODO: Implement logic (job) once the BE is done.
     */
    const saveBtnClicked = (): void => {
      if (state.numberOfBusinessesRef.validate()) {
        staffStore.updateDissolutionBatchSize(state.numberOfBusinesses)
        triggerEditOnOff()
      }
    }

    /** The array of validations rule(s) for the Dissolution Batch Size text field. */
    const dissolutionBatchSizeRules = computed(() => {
      return [
        v => !!v || 'The number of businesses to be moved into D1 dissolution per batch. Maximum of 600.',
        v => (v % 1 === 0) || 'Enter a whole number between 0 and 600.',
        v => v >= 0 || 'Enter a whole number between 0 and 600.',
        v => v <= 600 || 'Exceeds the maximum of 600 businesses per batch.'
      ]
    })

    /** The action button text depending on whether the dissolution job is paused or running. */
    const actionBtnText = computed(() => {
      return state.isOnHold ? 'Resume' : 'Pause'
    })

    /**
     * If non-edit, show the number of businesses into D1 from the store.
     * Otherwise, it'll be reactive to whatever is being typed in the text field.
     */
    const scheduleSummaryNumber = computed(() => {
      return state.isEdit ? state.numberOfBusinesses : staffStore.getDissolutionBatchSize()
    })

    return {
      ...toRefs(state),
      actionBtnClicked,
      actionBtnText,
      dissolutionBatchSizeRules,
      triggerEditOnOff,
      saveBtnClicked,
      scheduleSummaryNumber
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.section-container {
  color: $gray9;

  label {
    color: $gray9;
    font-weight: bold;
  }
}

// Vuetify Override of list item to change it's text and icon color to app blue
.theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  .v-icon.v-icon {
    color: $app-blue;
  }
}

// Adding shadows to buttons
.action-btn, .more-actions-btn {
    box-shadow: 0 1px 1px 0px rgb(0 0 0 / 20%), 0 2px 2px 0 rgb(0 0 0 / 14%), 0 1px 5px 0 rgb(0 0 0 / 12%);
    -webkit-box-shadow: 0 1px 1px 0px rgb(0 0 0 / 20%), 0 2px 2px 0 rgb(0 0 0 / 14%), 0 1px 5px 0 rgb(0 0 0 / 12%);
  }

// The action buttons styling (Pause, Resume)
.action-btn {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  min-width: 5.5rem !important;
  margin-right: 1px;
}

// The more actions button styling (chevron)
.more-actions-btn {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

// make menu button slightly smaller
.menu-btn {
  min-width: unset !important;
}

// Increasing dropdown menu (list) size to same size as button
.v-list {
  min-width: 8.5rem !important;
}

// Making the pencil icon smaller
.mdi-pencil:before, .mdi-pencil-set {
  font-size: $px-16;
}

// Increasing the Edit text size by a bit
.edit-txt {
  font-size: $px-14;
}

// Hiding the spin button of the v-text-field
::v-deep input::-webkit-outer-spin-button,
::v-deep input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
