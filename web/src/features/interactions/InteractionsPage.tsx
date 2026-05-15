import { useEffect, useState } from "react";
import { getOrganizations } from "../../api/client";
import type { OrganizationListItem } from "../../types";
import {
  createOrganizationInteraction,
  getOrganizationInteractions,
  updateInteraction,
} from "./api";
import { InteractionForm } from "./InteractionForm";
import { InteractionsTable } from "./InteractionsTable";
import type { InteractionCreate, InteractionItem, InteractionType } from "./types";
import "./interactions.css";

export function InteractionsPage() {
  const [organizations, setOrganizations] = useState<OrganizationListItem[]>([]);
  const [selectedOrganizationId, setSelectedOrganizationId] = useState("");
  const [interactions, setInteractions] = useState<InteractionItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOrganizations({ limit: 200, offset: 0 })
      .then((response) => {
        setOrganizations(response.items);

        if (response.items.length > 0) {
          setSelectedOrganizationId(response.items[0].id);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!selectedOrganizationId) {
      return;
    }

    loadInteractions(selectedOrganizationId);
  }, [selectedOrganizationId]);

  function loadInteractions(organizationId: string) {
    getOrganizationInteractions(organizationId)
      .then((items) => {
        setInteractions(items);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  function handleCreateInteraction(payload: InteractionCreate) {
    if (!selectedOrganizationId) {
      return;
    }

    createOrganizationInteraction(selectedOrganizationId, payload)
      .then(() => loadInteractions(selectedOrganizationId))
      .catch((err) => setError(err.message));
  }

  function handleChangeType(interactionId: string, type: InteractionType) {
    updateInteraction(interactionId, {
      interaction_type: type,
    })
      .then(() => loadInteractions(selectedOrganizationId))
      .catch((err) => setError(err.message));
  }

  const selectedOrganization = organizations.find(
    (organization) => organization.id === selectedOrganizationId
  );

  return (
    <div className="page">
      <h1>Взаимодействия</h1>

      {error && <div className="error">Ошибка: {error}</div>}

      <section className="section">
        <h2>Выбор организации</h2>

        <select
          className="organization-select"
          value={selectedOrganizationId}
          onChange={(event) => setSelectedOrganizationId(event.target.value)}
        >
          {organizations.map((organization) => (
            <option key={organization.id} value={organization.id}>
              {organization.name} {organization.bin ? `(${organization.bin})` : ""}
            </option>
          ))}
        </select>

        {selectedOrganization && (
          <p className="muted">
            Выбрана организация: <strong>{selectedOrganization.name}</strong>
          </p>
        )}
      </section>

      {selectedOrganizationId && (
        <>
          <section className="section">
            <h2>Новое взаимодействие</h2>

            <InteractionForm onSubmit={handleCreateInteraction} />
          </section>

          <section className="section">
            <h2>История взаимодействий</h2>

            <InteractionsTable
              items={interactions}
              onChangeType={handleChangeType}
            />
          </section>
        </>
      )}
    </div>
  );
}