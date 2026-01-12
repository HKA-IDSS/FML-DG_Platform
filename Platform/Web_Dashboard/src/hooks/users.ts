import { useQuery } from '@tanstack/react-query';
import api from 'api';
import { User } from 'api/models';

export function useUserName(userId?: string) {
    return useQuery<Pick<User, 'name'>, Error>({
        queryKey: ['user-name', userId],
        queryFn: async () => {
            const res = await api.getUserName(userId!);
            return res.data;
        },
        enabled: !!userId,
        staleTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
    });
}
