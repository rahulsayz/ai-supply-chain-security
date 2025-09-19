import { FastifySwaggerOptions } from '@fastify/swagger';
import { FastifySwaggerUiOptions } from '@fastify/swagger-ui';

export const swaggerOptions: FastifySwaggerOptions = {};

export const swaggerUiOptions: FastifySwaggerUiOptions = {
  routePrefix: '/documentation'
};
