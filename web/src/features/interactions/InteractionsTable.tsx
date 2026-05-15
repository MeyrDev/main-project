import type { InteractionItem, InteractionType } from "./types";

type Props = {
  items: InteractionItem[];
  onChangeType: (interactionId: string, type: InteractionType) => void;
};

export function InteractionsTable({ items, onChangeType }: Props) {
  if (items.length === 0) {
    return <p>По выбранной организации пока нет взаимодействий.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Дата</th>
          <th>Тип</th>
          <th>Тема</th>
          <th>Описание</th>
          <th>Изменить тип</th>
        </tr>
      </thead>

      <tbody>
        {items.map((interaction) => (
          <tr key={interaction.id}>
            <td>{new Date(interaction.happened_at).toLocaleString()}</td>
            <td>{interaction.interaction_type}</td>
            <td>{interaction.subject}</td>
            <td>{interaction.description ?? "-"}</td>
            <td>
              <select
                value={interaction.interaction_type}
                onChange={(event) =>
                  onChangeType(
                    interaction.id,
                    event.target.value as InteractionType
                  )
                }
              >
                <option value="call">call</option>
                <option value="email">email</option>
                <option value="meeting">meeting</option>
                <option value="note">note</option>
                <option value="task">task</option>
              </select>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}