import type {
  DealItem, 
  DealStage,
} from "../types/deals";
import { useEffect, useState, type FC, type SyntheticEvent } from "react";
import {
  createOrganizationDeal,
  getOrganizationDeals,
  updateDeal,
} from "../api/client";
import { toNumberOrNull, toStringOrNull } from "../utils";

type DealFormState = {
  title: string;
  stage: DealStage;
  amount: string;
  currency: string;
  expected_close_date: string;
  description: string;
};

const initialDealForm: DealFormState = {
  title: "",
  stage: "new",
  amount: "",
  currency: "KZT",
  expected_close_date: "2026-07-01",
  description: "",
};

type Props = {
  organizationId: string;
  loadData: () => void;
  setError: (message: string) => void;
};

export const Deals: FC<Props> = ({ organizationId, loadData, setError }) => {
  const [deals, setDeals] = useState<DealItem[]>([]);
  const [dealForm, setDealForm] = useState<DealFormState>(initialDealForm);

  function updateDealFormField(field: keyof DealFormState, value: string) {
    setDealForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleCreateDeal(event: SyntheticEvent) {
    event.preventDefault();

    createOrganizationDeal(organizationId, {
      owner_id: null,
      title: dealForm.title.trim(),
      stage: dealForm.stage,
      amount: toNumberOrNull(dealForm.amount),
      currency: dealForm.currency.trim() || "KZT",
      expected_close_date: toStringOrNull(dealForm.expected_close_date),
      description: toStringOrNull(dealForm.description),
    })
      .then(() => {
        setDealForm(initialDealForm);
        loadData();
        getOrganizationDeals(organizationId).then(setDeals)
      })
      .catch((err) => setError(err.message));
  }

  function handleChangeDealStage(dealId: string, stage: DealStage) {
    updateDeal(dealId, {
      stage,
      closed_at: stage === "closed" ? new Date().toISOString() : null,
    })
      .then(() => loadData())
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    getOrganizationDeals(organizationId).then(setDeals);
  }, [organizationId]);

  return (
    <section className="section">
      <h2>Сделки</h2>

      <form className="deal-form" onSubmit={handleCreateDeal}>
        <label>
          Название сделки
          <input
            value={dealForm.title}
            onChange={(event) =>
              updateDealFormField("title", event.target.value)
            }
            placeholder="Договор на поставку услуг"
            required
          />
        </label>

        <label>
          Стадия
          <select
            value={dealForm.stage}
            onChange={(event) =>
              updateDealFormField("stage", event.target.value as DealStage)
            }
          >
            <option value="new">new</option>
            <option value="negotiation">negotiation</option>
            <option value="approved">approved</option>
            <option value="rejected">rejected</option>
            <option value="closed">closed</option>
          </select>
        </label>

        <label>
          Сумма
          <input
            value={dealForm.amount}
            onChange={(event) =>
              updateDealFormField("amount", event.target.value)
            }
            placeholder="15000000"
          />
        </label>

        <label>
          Валюта
          <input
            value={dealForm.currency}
            onChange={(event) =>
              updateDealFormField("currency", event.target.value)
            }
            placeholder="KZT"
          />
        </label>

        <label>
          Ожидаемая дата закрытия
          <input
            type="date"
            value={dealForm.expected_close_date}
            onChange={(event) =>
              updateDealFormField("expected_close_date", event.target.value)
            }
          />
        </label>

        <label>
          Описание
          <input
            value={dealForm.description}
            onChange={(event) =>
              updateDealFormField("description", event.target.value)
            }
            placeholder="Описание сделки"
          />
        </label>

        <button type="submit">Создать сделку</button>
      </form>

      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Стадия</th>
            <th>Сумма</th>
            <th>Валюта</th>
            <th>Дата закрытия</th>
            <th>Действие</th>
          </tr>
        </thead>

        <tbody>
          {deals.map((deal) => (
            <tr key={deal.id}>
              <td>{deal.title}</td>
              <td>{deal.stage}</td>
              <td>{deal.amount ?? "-"}</td>
              <td>{deal.currency}</td>
              <td>{deal.expected_close_date ?? "-"}</td>
              <td>
                <select
                  value={deal.stage}
                  onChange={(event) =>
                    handleChangeDealStage(
                      deal.id,
                      event.target.value as DealStage,
                    )
                  }
                >
                  <option value="new">new</option>
                  <option value="negotiation">negotiation</option>
                  <option value="approved">approved</option>
                  <option value="rejected">rejected</option>
                  <option value="closed">closed</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};
