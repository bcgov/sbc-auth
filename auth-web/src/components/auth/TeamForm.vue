<template>
  <div>
    <div v-if="organizations.length > 0">
      You already belong to a team: <span class="font-weight-bold">{{ organizations[0].name }}</span>
      <v-row>
        <v-col cols="12" class="form__btns pb-0">
          <v-btn large color="primary" @click="redirectToNext">
            Next
          </v-btn>
        </v-col>
      </v-row>
    </div>
    <div>
      <h2 class="mb-6">Your Team Name</h2>
      <v-form v-if="organizations.length === 0" ref="createTeamForm">
        <v-radio-group class="mb-3" v-model="teamType" :mandatory="true">
          <v-radio class="mb-3" label="I manage my own business" value="BASIC"/>
          <v-radio label="I manage multiple businesses on behalf of my clients" value="PREMIUM" />
        </v-radio-group>
        <v-text-field filled :rules="teamNameRules" v-model="teamName" :label="teamType === 'BASIC' ? 'Your Business Name' : 'Your Management Company or Law Firm Name'" />
        <v-row>
          <v-col cols="12" class="form__btns pb-0">
            <v-btn large color="primary" class="mr-2" :disabled='!isFormValid()' @click="save">
              Save and Continue
            </v-btn>
            <v-btn large color="default" @click="cancel">
              Cancel
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['organizations'])
  },
  methods: {
    ...mapActions('org', ['createOrg']),
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class TeamForm extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private teamName: string = ''
  private teamType: string = 'BASIC'
  private readonly organizations!: Organization[]
  private readonly createOrg!: (requestBody: CreateRequestBody) => Organization
  private readonly syncOrganizations!: () => Organization[]

  $refs: {
    createTeamForm: HTMLFormElement
  }

  private readonly teamNameRules = [
    v => !!v || 'You must provide a team name'
  ]

  private async mounted () {
    if (!this.organizations) {
      await this.syncOrganizations()
    }
  }

  private isFormValid (): boolean {
    return !!this.teamName
  }

  private async save () {
    // Validate form, and then create an team with this user a member
    if (this.isFormValid()) {
      const createRequestBody: CreateRequestBody = {
        name: this.teamName,
        typeCode: this.teamType === 'BASIC' ? 'IMPLICIT' : 'EXPLICIT'
      }

      try {
        await this.createOrg(createRequestBody)
        this.redirectToNext()
      } catch (exception) {
        // Handle error
        // eslint-disable-next-line no-console
        console.error(exception.error)
      }
    }
  }

  private cancel () {
    this.$router.push({ path: '/home' })
  }

  private redirectToNext () {
    this.$router.push({ path: '/main' })
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  // Tighten up some of the spacing between rows
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }
</style>
