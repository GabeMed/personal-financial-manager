import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/services/apiClient";
import type { TransactionDTO } from "@/types";
import type { NewTransactionDTO } from "@/schemas/transaction";
import useCreateCategory from "./useCreateCategory";

export default function useUpdateTransaction() {
  const qc = useQueryClient();
  const createCategory = useCreateCategory();

  return useMutation<
    TransactionDTO,
    Error,
    { id: number; body: NewTransactionDTO }
  >({
    mutationFn: async ({ id, body }) => {
      // Same "+ New…" category flow as useAddFormTransaction: without it the
      // PATCH would send category_id: null.
      let category_id = body.category_id;
      if (category_id === null && body.newCategoryName) {
        const newCat = await createCategory.mutateAsync({
          name: body.newCategoryName,
        });
        category_id = newCat.id;
      }

      const { data } = await apiClient.patch<TransactionDTO>(
        `/transactions/${id}`,
        {
          description: body.description,
          amount: body.amount,
          type: body.type,
          category_id,
        }
      );
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["summary"] });
    },
  });
}
