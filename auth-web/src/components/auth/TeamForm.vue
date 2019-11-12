<template>
  <div>
    <div class="v-form" v-if="organizations.length > 0">
      You already belong to a team: <span class="font-weight-bold">{{ organizations[0].name }}</span>
      <v-row>
        <v-col cols="12" class="form__btns pb-0">
          <v-btn large color="primary" @click="redirectToNext">
            Next
          </v-btn>
        </v-col>
      </v-row>
    </div>
    <v-form v-if="organizations.length === 0" ref="createTeamForm">
      <v-radio-group v-model="teamType" :mandatory="true">
        <v-radio class="mb-5" label="I manage my own business" value="BASIC"/>
        <v-radio label="I manage businesses on behalf of my clients" value="PREMIUM" />
      </v-radio-group>
      <div class="mt-5">
        <h3 v-if="teamType === 'BASIC'">Your Team Name</h3>
        <h3 v-if="teamType === 'PREMIUM'">Your Organization Name</h3>
        <v-text-field :rules="teamNameRules" placeholder="Team Name" v-model="teamName" />
      </div>
      <v-row>
        <v-col cols="12" class="form__btns pb-0">
          <v-btn large color="primary" class="mr-2" :disabled='!isFormValid()' @click="save">
            Next
          </v-btn>
          <v-btn large color="secondary" @click="cancel">
            Cancel
          </v-btn>
        </v-col>
      </v-row>
    </v-form>
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
  .v-form {
    padding: 1.5rem;

    .form__btns {
      display: flex;
      justify-content: flex-end;
    }
  }
</style>
