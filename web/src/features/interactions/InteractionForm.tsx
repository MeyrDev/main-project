import { useState, type SyntheticEvent } from "react";
import type { InteractionCreate, InteractionType } from "./types";

type Props = {
  onSubmit: (payload: InteractionCreate) => void;
};

type FormState = {
  interaction_type: InteractionType;
  subject: string;
  description: string;
  happened_at: string;
};

const initialForm: FormState = {
  interaction_type: "call",
  subject: "",
  description: "",
  happened_at: new Date().toISOString().slice(0, 16),
};

export function InteractionForm({ onSubmit }: Props) {
  const [form, setForm] = useState<FormState>(initialForm);

  function updateField(field: keyof FormState, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    onSubmit({
      user_id: null,
      deal_id: null,
      interaction_type: form.interaction_type,
      subject: form.subject.trim(),
      description: form.description.trim() || null,
      happened_at: new Date(form.happened_at).toISOString(),
    });

    setForm(initialForm);
  }

  return (
    <form className="interaction-form" onSubmit={handleSubmit}>
      <label>
        Тип
        <select
          value={form.interaction_type}
          onChange={(event) =>
            updateField("interaction_type", event.target.value as InteractionType)
          }
        >
          <option value="call">Звонок</option>
          <option value="email">Email</option>
          <option value="meeting">Встреча</option>
          <option value="note">Заметка</option>
          <option value="task">Задача</option>
        </select>
      </label>

      <label>
        Тема
        <input
          value={form.subject}
          onChange={(event) => updateField("subject", event.target.value)}
          placeholder="Первичный звонок клиенту"
          required
        />
      </label>

      <label>
        Дата и время
        <input
          type="datetime-local"
          value={form.happened_at}
          onChange={(event) => updateField("happened_at", event.target.value)}
          required
        />
      </label>

      <label>
        Описание
        <input
          value={form.description}
          onChange={(event) => updateField("description", event.target.value)}
          placeholder="Краткое описание взаимодействия"
        />
      </label>

      <button type="submit">Добавить взаимодействие</button>
    </form>
  );
}