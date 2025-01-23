<template>
  <div>
    <p
      v-if="canSelect"
      class="mb-9"
    >
      General Ledger codes for the account that is issued by the Finance department of the Ministry
    </p>
    <v-form ref="GlInfoForm">
      <section>
        <header class="mb-4 d-flex align-content-center">
          <div
            data-test="pad-info-form-title"
            class="mr-1 font-weight-bold"
          >
            General Ledger Information
          </div>
        </header>
        <v-row>
          <v-col
            cols="4"
            class="py-0"
          >
            <v-text-field
              v-model="client"
              v-mask="'XXX'"
              label="Client Code"
              filled
              hint="3 characters"
              persistent-hint
              :rules="clientRules"
              data-test="input-client-code"
              :disabled="!canSelect"
            />
          </v-col>
          <v-col
            cols="4"
            class="py-0"
          >
            <v-text-field
              v-model="responsibilityCentre"
              v-mask="'XXXXX'"
              label="Responsibility Center"
              filled
              hint="5 characters"
              persistent-hint
              :rules="responsibilityCentreRules"
              data-test="input-responsibilityCentre"
              :disabled="!canSelect"
            />
          </v-col>
          <v-col
            cols="4"
            class="py-0"
          >
            <v-text-field
              v-model="serviceLine"
              v-mask="'XXXXX'"
              label="Account Number"
              filled
              hint="5 characters"
              persistent-hint
              :rules="serviceLineRules"
              data-test="input-serviceLine"
              :disabled="!canSelect"
            />
          </v-col>
          <v-col
            cols="4"
            class="py-0"
          >
            <v-text-field
              v-model="stob"
              v-mask="'XXXX'"
              label="Standard Object"
              filled
              hint="4 characters"
              persistent-hint
              :rules="stobRules"
              data-test="input-stob"
              :disabled="!canSelect"
            />
          </v-col>
          <v-col
            cols="8"
            class="py-0"
          >
            <v-text-field
              v-model="projectCode"
              v-mask="'XXXXXXX'"
              label="Project"
              filled
              hint="7 characters"
              persistent-hint
              :rules="projectCodeRules"
              data-test="input-projectCode"
              :disabled="!canSelect"
            />
          </v-col>
        </v-row>
      </section>
    </v-form>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { GLInfo } from '@/models/Organization'
import { mask } from 'vue-the-mask'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  directives: {
    mask
  },
  props: {
    glInformation: {
      type: Object,
      default: () => ({ client: '', responsibilityCentre: '', serviceLine: '', stob: '', projectCode: '' } as GLInfo)
    },
    canSelect: {
      type: Boolean,
      default: true
    }
  },
  emits: ['is-gl-info-form-valid'],
  setup (props, { emit }) {
    const orgStore = useOrgStore()
    const GlInfoForm = ref(null) as HTMLFormElement

    const state = reactive({
      client: '',
      responsibilityCentre: '',
      serviceLine: '',
      stob: '',
      projectCode: '',
      clientRules: [
        v => !!v || 'Client Code is required',
        v => (v.length >= 3) || 'Client Code should be 3 characters'
      ],
      responsibilityCentreRules: [
        v => !!v || 'Responsibility Center is required',
        v => (v.length === 5) || 'Responsibility Center should be 5 characters'
      ],
      serviceLineRules: [
        v => !!v || 'Account Number is required',
        v => (v.length === 5) || 'Account Number should be 5 characters'
      ],
      stobRules: [
        v => !!v || 'Standard Object is required',
        v => (v.length === 4) || 'Standard Object should be 4 characters'
      ],
      projectCodeRules: [
        v => !!v || 'Project is required',
        v => (v.length === 7) || 'Project should be 7 characters'
      ]
    })

    function setGlInfo (glInfo) {
      state.client = glInfo?.client || ''
      state.responsibilityCentre = glInfo?.responsibilityCentre || ''
      state.serviceLine = glInfo?.serviceLine || ''
      state.stob = glInfo?.stob || ''
      state.projectCode = glInfo?.projectCode || ''
    }

    async function emitGLInfo () {
      const glInfo: GLInfo = {
        client: state.client,
        responsibilityCentre: state.responsibilityCentre,
        serviceLine: state.serviceLine,
        stob: state.stob,
        projectCode: state.projectCode
      }
      isGlInfoFormValid()
      orgStore.setCurrentOrganizationGLInfo(glInfo)
      return glInfo
    }

    function isGlInfoFormValid () {
      const isGLInfoValid = GlInfoForm.value?.validate() || false
      // emit to enable next button
      emit('is-gl-info-form-valid', isGLInfoValid)
      return isGLInfoValid
    }

    watch(() => orgStore.currentOrgGLInfo, (newGlInfo) => {
      setGlInfo(newGlInfo)
    })

    watch(() => [state.client, state.responsibilityCentre, state.serviceLine, state.stob, state.projectCode], () => {
      emitGLInfo()
    })

    onMounted(() => {
      const glInfo: GLInfo = (Object.keys(props.glInformation).length) ? props.glInformation as GLInfo : orgStore.currentOrgGLInfo
      setGlInfo(glInfo)
    })

    return {
      ...toRefs(state),
      GlInfoForm,
      emitGLInfo,
      isGlInfoFormValid
    }
  }
})
</script>
