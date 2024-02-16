<template>
  <section>
    <h2 class="mb-3">
      {{ `${tabNumber !== null ? `${tabNumber}. ` : ''}${title}` }}
    </h2>
    <v-row v-if="accountUnderReview.orgType === Account.BASIC">
      <v-col class="col-12 col-sm-3">
        Account Name
      </v-col>
      <v-col>
        {{ accountUnderReview.name }}
      </v-col>
    </v-row>
    <!-- for GOVM account showing banch name  -->
    <v-row v-else-if="accountUnderReview.orgType === Account.PREMIUM && accountUnderReview.accessType === AccessType.GOVM">
      <v-col class="col-12 col-sm-3">
        <span> Account Name <br> &amp; Branch Details</span>
      </v-col>
      <v-col>
        <v-alert
          dark
          color="primary"
          class="bcol-acc mb-0 px-7 py-5"
        >
          <div class="bcol-acc__name mt-n1">
            {{ accountUnderReview.name }}
          </div>
          <ul class="bcol-acc__meta">
            <li>
              Branch Name : {{ accountUnderReview.branchName }}
            </li>
          </ul>
        </v-alert>
      </v-col>
    </v-row>
    <!-- all other accounts -->
    <v-row v-else>
      <v-col class="col-12 col-sm-3">
        <span>Account Name <br> &amp; BC Online Details</span>
      </v-col>
      <v-col>
        <v-alert
          dark
          color="primary"
          class="bcol-acc mb-0 px-7 py-5"
        >
          <div class="bcol-acc__name mt-n1">
            {{ accountUnderReview.name }}
          </div>
          <ul
            v-if="accountUnderReview.bcolAccountId"
            class="bcol-acc__meta"
          >
            <li>
              Account No: {{ accountUnderReview.bcolAccountId }}
            </li>
            <li>
              Prime Contact ID: {{ accountUnderReview.bcolUserId }}
            </li>
          </ul>
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-if="accountUnderReviewAddress">
      <v-col class="col-12 col-sm-3">
        Mailing Address
      </v-col>
      <v-col>
        <ul class="mailing-address">
          <li>{{ accountUnderReviewAddress.street }}</li>
          <li>
            {{ accountUnderReviewAddress.city }}
            {{ accountUnderReviewAddress.region }}
            {{ accountUnderReviewAddress.postalCode }}
          </li>
          <li>{{ accountUnderReviewAddress.country }}</li>
        </ul>
      </v-col>
    </v-row>
    <v-row
      v-if="isGovnReview"
      class="access-type"
      :class="showValidations && editing ? 'error-border': ''"
    >
      <v-col class="col-12 col-sm-3">
        <p :class="showValidations && editing ? 'error-color ma-0': 'ma-0'">
          Access Type
        </p>
        <v-chip
          v-if="changedAccess"
          color="primary"
          label
          text-color="white"
        >
          CHANGED
        </v-chip>
      </v-col>
      <v-col>
        <v-row
          v-if="!editing"
          no-gutters
        >
          <v-col class="access-type__desc">
            {{ accessTypeDesc }}
          </v-col>
          <v-col
            v-if="accountUnderReview.accessType === AccessType.GOVN"
            cols="auto"
          >
            <v-btn
              v-if="changedAccess"
              class="access-type__btn"
              color="primary"
              text
              @click="resetAccess()"
            >
              <v-icon
                class="mr-1"
                color="primary"
                size="16"
              >
                mdi-undo
              </v-icon>Undo
            </v-btn>
            <v-btn
              v-else
              class="access-type__btn"
              color="primary"
              text
              @click="editing=true"
            >
              <v-icon
                class="mr-1"
                color="primary"
                size="16"
              >
                mdi-pencil
              </v-icon>Change
            </v-btn>
          </v-col>
        </v-row>
        <div
          v-else
          no-gutters
        >
          <v-radio-group
            v-model="selectedAccessType"
            class="access-type__radio-grp mt-0"
            hide-details
          >
            <v-radio
              :key="AccessType.REGULAR"
              label="Regular Access"
              :value="AccessType.REGULAR"
            />
            <v-radio
              :key="AccessType.GOVN"
              label="Government agency (other than BC provincial)"
              :value="AccessType.GOVN"
            />
          </v-radio-group>
          <p
            v-if="selectedAccessType == AccessType.REGULAR"
            class="mt-5"
          >
            Regular access will not have the option to modify product fees.
          </p>
          <v-row
            class="mt-7"
            justify="end"
            no-gutters
          >
            <v-col
              class="mr-3"
              cols="auto"
            >
              <v-btn
                class="px-9"
                color="primary"
                @click="updateAccess()"
              >
                Done
              </v-btn>
            </v-col>
            <v-col cols="auto">
              <v-btn
                class="px-9"
                color="primary"
                outlined
                @click="cancelEdit()"
              >
                Cancel
              </v-btn>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>
  </section>
</template>

<script lang="ts">
import { AccessType, Account, TaskType } from '@/util/constants'
import { computed, defineComponent, ref, watch } from '@vue/composition-api'
import { Address } from '@/models/address'
import { Organization } from '@/models/Organization'

export default defineComponent({
  name: 'AccountInformation',
  props: {
    tabNumber: { type: Number, default: null },
    title: { type: String, default: 'Account Information' },
    accountUnderReview: { default: null as Organization },
    accountUnderReviewAddress: { default: null as Address },
    isGovnReview: { type: Boolean, default: false },
    showValidations: { type: Boolean, default: false }
  },
  emits: ['emit-access-type', 'emit-valid'],
  setup (props, { emit }) {
    const changedAccess = ref(false)

    const selectedAccessType = ref(props.accountUnderReview.accessType as AccessType)
    watch(() => props.accountUnderReview.accessType, (val) => { selectedAccessType.value = val as AccessType })

    const accessTypeDesc = computed((): string => {
      switch (selectedAccessType.value) {
        case AccessType.GOVN:
          return 'Government agency (other than BC provincial)'
        case AccessType.GOVM:
          return 'BC Government Ministry'
        default:
          return 'Regular Access'
      }
    })

    const editing = ref(false)
    watch(() => editing.value, (val) => { emit('emit-valid', !val) }) // invalid if editing

    const cancelEdit = () => {
      editing.value = false
      selectedAccessType.value = props.accountUnderReview.accessType as AccessType
    }

    const updateAccess = () => {
      changedAccess.value = selectedAccessType.value !== props.accountUnderReview.accessType
      editing.value = false
      emit('emit-access-type', selectedAccessType.value)
    }

    const resetAccess = () => {
      selectedAccessType.value = props.accountUnderReview.accessType as AccessType
      updateAccess()
    }
    return {
      AccessType,
      Account,
      TaskType,
      accessTypeDesc,
      editing,
      changedAccess,
      selectedAccessType,
      cancelEdit,
      resetAccess,
      updateAccess
    }
  }
})
</script>

<style lang="scss" scoped>
  .access-type {

    &__btn {
      height: 20px !important;
      margin-top: -2px;
    }
  }
  // BC Online Account Information
  .bcol-acc__name {
    font-size: 1.125rem;
    font-weight: 700;
  }

  .bcol-acc__meta {
    margin: 0;
    padding: 0;
    list-style-type: none;
    font-size: .925rem;

    li {
      position: relative;
      display: inline-block
    }

    li + li {
      &:before {
        content: ' | ';
        display: inline-block;
        position: relative;
        top: -2px;
        left: 2px;
        width: 2rem;
        vertical-align: top;
        text-align: center;
      }
    }
  }

  .error-border { border-left: 2px solid var(--v-error-base); }
  .error-color { color: var(--v-error-base) }

  .mailing-address {
    list-style-type: none;
    margin: 0;
    padding: 0;
  }

  .v-chip.v-size--default {
    font-size: 0.625rem;
    height: 20px;
  }

</style>
