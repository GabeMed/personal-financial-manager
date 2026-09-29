export interface CategoryDTO {
  id: number;
  name: string;
}

export type TransactionType = "income" | "expense";

export interface TransactionDTO {
  id: number;
  description: string;
  amount: number;
  type: TransactionType;
  category: CategoryDTO;
  date: string;
}

export interface SummaryDTO {
  balance: number;
  income_total: number;
  expense_total: number;
  income_porcentage_by_category: Record<string, number>; // { "CategoryId": Percentage }
  expense_porcentage_by_category: Record<string, number>;
}
