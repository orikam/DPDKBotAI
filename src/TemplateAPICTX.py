ctx = """
Configuration
~~~~~~~~~~~~~

This function performs the flow API engine configuration and allocates
requested resources beforehand to avoid costly allocations later.
Expected number of resources in an application allows PMD to prepare
and optimize NIC hardware configuration and memory layout in advance.
``rte_flow_configure()`` must be called before any flow rule is created,
but after an Ethernet device is configured.
It also creates flow queues for asynchronous flow rules operations via
queue-based API, see `Asynchronous operations`_ section.

.. code-block:: c

   int
   rte_flow_configure(uint16_t port_id,
                      const struct rte_flow_port_attr *port_attr,
                      uint16_t nb_queue,
                      const struct rte_flow_queue_attr *queue_attr[],
                      struct rte_flow_error *error);

Information about the number of available resources can be retrieved via
``rte_flow_info_get()`` API.

.. code-block:: c

   int
   rte_flow_info_get(uint16_t port_id,
                     struct rte_flow_port_info *port_info,
                     struct rte_flow_queue_info *queue_info,
                     struct rte_flow_error *error);

Group Miss Actions
~~~~~~~~~~~~~~~~~~

In an application, many flow rules share common group attributes, meaning they can be grouped and
classified together. A user can explicitly specify a set of actions performed on a packet when it
did not match any flows rules in a group using the following API:

.. code-block:: c

      int
      rte_flow_group_set_miss_actions(uint16_t port_id,
                                      uint32_t group_id,
                                      const struct rte_flow_group_attr *attr,
                                      const struct rte_flow_action actions[],
                                      struct rte_flow_error *error);

For example, to configure a RTE_FLOW_TYPE_JUMP action as a miss action for ingress group 1:

.. code-block:: c

      struct rte_flow_group_attr attr = {.ingress = 1};
      struct rte_flow_action act[] = {
      /* Setting miss actions to jump to group 3 */
          [0] = {.type = RTE_FLOW_ACTION_TYPE_JUMP,
                 .conf = &(struct rte_flow_action_jump){.group = 3}},
          [1] = {.type = RTE_FLOW_ACTION_TYPE_END},
      };
      struct rte_flow_error err;
      rte_flow_group_set_miss_actions(port, 1, &attr, act, &err);

.. _flow_templates:

Flow templates
~~~~~~~~~~~~~~

Oftentimes in an application, many flow rules share a common structure
(the same pattern and/or action list) so they can be grouped and classified
together. This knowledge may be used as a source of optimization by a PMD/HW.
The flow rule creation is done by selecting a table, a pattern template
and an actions template (which are bound to the table), and setting unique
values for the items and actions. This API is not thread-safe.

Pattern templates
^^^^^^^^^^^^^^^^^

The pattern template defines a common pattern (the item mask) without values.
The mask value is used to select a field to match on, spec/last are ignored.
The pattern template may be used by multiple tables and must not be destroyed
until all these tables are destroyed first.

.. code-block:: c

   struct rte_flow_pattern_template *
   rte_flow_pattern_template_create(uint16_t port_id,
       const struct rte_flow_pattern_template_attr *template_attr,
       const struct rte_flow_item pattern[],
       struct rte_flow_error *error);

For example, to create a pattern template to match on the destination MAC:

.. code-block:: c

   const struct rte_flow_pattern_template_attr attr = {.ingress = 1};
   struct rte_flow_item_eth eth_m = {
       .dst.addr_bytes = { 0xff, 0xff, 0xff, 0xff, 0xff, 0xff };
   };
   struct rte_flow_item pattern[] = {
       [0] = {.type = RTE_FLOW_ITEM_TYPE_ETH,
              .mask = &eth_m},
       [1] = {.type = RTE_FLOW_ITEM_TYPE_END,},
   };
   struct rte_flow_error err;

   struct rte_flow_pattern_template *pattern_template =
           rte_flow_pattern_template_create(port, &attr, &pattern, &err);

The concrete value to match on will be provided at the rule creation.

Actions templates
^^^^^^^^^^^^^^^^^

The actions template holds a list of action types to be used in flow rules.
The mask parameter allows specifying a shared constant value for every rule.
if the action has a different value for every rule then the mask should be set to 0 or NULL.
The actions template may be used by multiple tables and must not be destroyed
until all these tables are destroyed first.

.. code-block:: c

   struct rte_flow_actions_template *
   rte_flow_actions_template_create(uint16_t port_id,
       const struct rte_flow_actions_template_attr *template_attr,
       const struct rte_flow_action actions[],
       const struct rte_flow_action masks[],
       struct rte_flow_error *error);

For example, to create an actions template with the same Mark ID
but different Queue Index for every rule:

.. code-block:: c

   rte_flow_actions_template_attr attr = {.ingress = 1};
   struct rte_flow_action act[] = {
   /* Mark ID is 4 for every rule, Queue Index is unique */
       [0] = {.type = RTE_FLOW_ACTION_TYPE_MARK,
              .conf = &(struct rte_flow_action_mark){.id = 4}},
       [1] = {.type = RTE_FLOW_ACTION_TYPE_QUEUE},
       [2] = {.type = RTE_FLOW_ACTION_TYPE_END,},
   };
   struct rte_flow_action msk[] = {
   /* Assign to MARK mask any non-zero value to make it constant */
       [0] = {.type = RTE_FLOW_ACTION_TYPE_MARK,
              .conf = &(struct rte_flow_action_mark){.id = 1}},
       [1] = {.type = RTE_FLOW_ACTION_TYPE_QUEUE},
       [2] = {.type = RTE_FLOW_ACTION_TYPE_END,},
   };
   struct rte_flow_error err;

   struct rte_flow_actions_template *actions_template =
           rte_flow_actions_template_create(port, &attr, &act, &msk, &err);

The concrete value for Queue Index will be provided at the rule creation.

Template table
^^^^^^^^^^^^^^

A template table combines a number of pattern and actions templates along with
shared flow rule attributes (group ID, priority and traffic direction).
This way a PMD/HW can prepare all the resources needed for efficient flow rules
creation in the datapath. To avoid any hiccups due to memory reallocation,
the maximum number of flow rules is defined at table creation time.
Any flow rule creation beyond the maximum table size is rejected.
Application may create another table to accommodate more rules in this case.

.. code-block:: c

   struct rte_flow_template_table *
   rte_flow_template_table_create(uint16_t port_id,
       const struct rte_flow_template_table_attr *table_attr,
       struct rte_flow_pattern_template *pattern_templates[],
       uint8_t nb_pattern_templates,
       struct rte_flow_actions_template *actions_templates[],
       uint8_t nb_actions_templates,
       struct rte_flow_error *error);

A table can be created only after the Flow Rules management is configured
and pattern and actions templates are created.

.. code-block:: c

   rte_flow_template_table_attr table_attr = {
       .flow_attr.ingress = 1,
       .nb_flows = 10000;
   };
   uint8_t nb_pattern_templ = 1;
   struct rte_flow_pattern_template *pattern_templates[nb_pattern_templ];
   pattern_templates[0] = pattern_template;
   uint8_t nb_actions_templ = 1;
   struct rte_flow_actions_template *actions_templates[nb_actions_templ];
   actions_templates[0] = actions_template;
   struct rte_flow_error error;

   struct rte_flow_template_table *table =
           rte_flow_template_table_create(port, &table_attr,
                   &pattern_templates, nb_pattern_templ,
                   &actions_templates, nb_actions_templ,
                   &error);

Table Attribute: Specialize
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Application can help optimizing underlayer resources and insertion rate
by specializing template table.
Specialization is done by providing hints
in the template table attribute ``specialize``.

This attribute is not mandatory for driver to implement.
If a hint is not supported, it will be silently ignored,
and no special optimization is done.

If a table is specialized, the application should make sure the rules
comply with the table attribute.
The application functionality must not rely on the hints,
they are not replacing the matching criteria of flow rules.

Template table resize
^^^^^^^^^^^^^^^^^^^^^

The resizable template table API enables applications to dynamically adjust
capacity of template tables without disrupting the existing flow rules operation.
The resizable template table API allows applications to optimize
the memory usage and performance of template tables
according to the traffic conditions and requirements.

A typical use case for the resizable template table API:

  #. Create a resizable table with the initial capacity.
  #. Change the table flow rules capacity.
  #. Update table flow objects.
  #. Complete the table resize.

A resizable table can be either in normal or resizable state.
When application begins to resize the table, its state is changed to resizable.
The table stays in resizable state until the application finishes resize procedure.
The application can resize a table in the normal state only.

The application needs to set the ``RTE_FLOW_TABLE_SPECIALIZE_RESIZABLE`` bit in
the table attributes when creating a template table that can be resized,
and the bit cannot be set or cleared later.

The application triggers the table resize by calling
the ``rte_flow_template_table_resize()`` function.
The resize process updates the table configuration to fit the new flow rules capacity.
Table resize does not change existing flow objects configuration.
The application can create new flow rules and modify or delete
existing flow rules while the table is resizing,
but the table performance might be slower than usual.

Flow rules that existed before table resize are fully functional after table resize.
However, the application must update flow objects to match the new table configuration.
The application calls ``rte_flow_async_update_resized()`` to update flow object
for the new table configuration.
It should be called for flow rules created before table resize.
If called for flow rules created after table resize, the call should return success.
The application is free to call this API for all table flow rules.

The application calls ``rte_flow_template_table_resize_complete()``
to return a table to normal state after it completed flow objects update.

Testpmd commands (wrapped for clarity)::

    # 1. Create resizable template table for 1 flow.
    testpmd> flow pattern_template 0 create ingress pattern_template_id 3
                  template eth / ipv4 / udp src mask 0xffff / end
    testpmd> flow actions_template 0 create ingress actions_template_id 7
                  template count  / rss / end
    testpmd> flow template_table 0 create table_id 101 resizable ingress
                  group 1 priority 0 rules_number 1
                  pattern_template 3 actions_template 7

    # 2. Queue a flow rule.
    testpmd> flow queue 0 create 0 template_table 101
                  pattern_template 0 actions_template 0 postpone no
                  pattern eth / ipv4 / udp src spec 1 / end actions count / rss / end

    # 3. Resize the template table
    #    The new table capacity is 32 rules
    testpmd> flow template_table 0 resize table_resize_id 101
                  table_resize_rules_num 32

    # 4. Queue more flow rules.
    testpmd> flow queue 0 create 0 template_table 101
                  pattern_template 0 actions_template 0 postpone no
                  pattern eth / ipv4 / udp src spec 2 / end actions count / rss / end
    testpmd> flow queue 0 create 0 template_table 101
                  pattern_template 0 actions_template 0 postpone no
                  pattern eth / ipv4 / udp src spec 3 / end actions count / rss / end
    testpmd> flow queue 0 create 0 template_table 101
                  pattern_template 0 actions_template 0 postpone no
                  pattern eth / ipv4 / udp src spec 4 / end actions count / rss / end

    # 5. Queue flow rules updates.
    # Rule 0 was created before table resize - must be updated.
    testpmd> flow queue 0 update_resized 0 rule 0
    # Rule 1 was created after table resize - flow pull returns success.
    testpmd> flow queue 0 update_resized 0 rule 1

    # 6. Complete the table resize.
    testpmd> flow template_table 0 resize_complete table 101

Asynchronous operations
-----------------------

Flow rules management can be done via special lockless flow management queues.

- Queue operations are asynchronous and not thread-safe.

- Operations can thus be invoked by the app's datapath,
  packet processing can continue while queue operations are processed by NIC.

- Number of flow queues is configured at initialization stage.

- Available operation types: rule creation, rule destruction,
  indirect rule creation, indirect rule destruction, indirect rule update.

- Operations may be reordered within a queue.

- Operations can be postponed and pushed to NIC in batches.

- Results pulling must be done on time to avoid queue overflows.

- User data is returned as part of the result to identify an operation.

- Flow handle is valid once the creation operation is enqueued and must be
  destroyed even if the operation is not successful and the rule is not inserted.

- Application must wait for the creation operation result before enqueueing
  the deletion operation to make sure the creation is processed by NIC.

The asynchronous flow rule insertion logic can be broken into two phases.

#. Initialization stage as shown here:

   .. _figure_rte_flow_async_init:

   .. figure:: ../img/rte_flow_async_init.*

#. Main loop as presented on a datapath application example:

   .. _figure_rte_flow_async_usage:

   .. figure:: ../img/rte_flow_async_usage.*

Enqueue creation operation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enqueueing a flow rule creation operation is similar to simple creation.

.. code-block:: c

   struct rte_flow *
   rte_flow_async_create(uint16_t port_id,
                         uint32_t queue_id,
                         const struct rte_flow_op_attr *op_attr,
                         struct rte_flow_template_table *template_table,
                         const struct rte_flow_item pattern[],
                         uint8_t pattern_template_index,
                         const struct rte_flow_action actions[],
                         uint8_t actions_template_index,
                         void *user_data,
                         struct rte_flow_error *error);

A valid handle in case of success is returned. It must be destroyed later
by calling ``rte_flow_async_destroy()`` even if the rule is rejected by HW.

Enqueue creation by index operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enqueueing a flow rule creation operation to insert a rule at a table index.

.. code-block:: c

   struct rte_flow *
   rte_flow_async_create_by_index(uint16_t port_id,
                                  uint32_t queue_id,
                                  const struct rte_flow_op_attr *op_attr,
                                  struct rte_flow_template_table *template_table,
                                  uint32_t rule_index,
                                  const struct rte_flow_action actions[],
                                  uint8_t actions_template_index,
                                  void *user_data,
                                  struct rte_flow_error *error);

A valid handle in case of success is returned. It must be destroyed later
by calling ``rte_flow_async_destroy()`` even if the rule is rejected by HW.

Enqueue creation by index with pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enqueueing a flow rule creation operation to insert a rule at a table index with pattern.

.. code-block:: c

   struct rte_flow *
   rte_flow_async_create_by_index_with_pattern(uint16_t port_id,
                                               uint32_t queue_id,
                                               const struct rte_flow_op_attr *op_attr,
                                               struct rte_flow_template_table *template_table,
                                               uint32_t rule_index,
                                               const struct rte_flow_item pattern[],
                                               uint8_t pattern_template_index,
                                               const struct rte_flow_action actions[],
                                               uint8_t actions_template_index,
                                               void *user_data,
                                               struct rte_flow_error *error);

Enqueue destruction operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enqueueing a flow rule destruction operation is similar to simple destruction.

.. code-block:: c

   int
   rte_flow_async_destroy(uint16_t port_id,
                          uint32_t queue_id,
                          const struct rte_flow_op_attr *op_attr,
                          struct rte_flow *flow,
                          void *user_data,
                          struct rte_flow_error *error);

Enqueue update operation
~~~~~~~~~~~~~~~~~~~~~~~~

Enqueueing a flow rule update operation to replace actions in the existing rule.

.. code-block:: c

   int
   rte_flow_async_actions_update(uint16_t port_id,
                                 uint32_t queue_id,
                                 const struct rte_flow_op_attr *op_attr,
                                 struct rte_flow *flow,
                                 const struct rte_flow_action actions[],
                                 uint8_t actions_template_index,
                                 void *user_data,
                                 struct rte_flow_error *error);

example testpmd command that matches on ipv4 udp traffic and sends it to queue 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// configure the port to work with rte_flow template api
flow configure 0 queues_number 2 queues_size 64 // if counters are needed then the number of counters should be added, before running this command the port must be stoped and started again after this command
//create the pattern template
flow pattern_template 0 create pattern_template_id 1 ingress  template eth / ipv4 / udp / end
//create the actions template 
flow actions_template 0 create ingress actions_template_id 1   template queue index 1 / end mask queue index 1 / end
//create the template table that holds 4 rules and is located in group 1
flow template_table 0 create table_id 1 priority 0 ingress rules_number 4 group 1 pattern_template 1 actions_template 1
//insert the rule to the template table
flow queue 0 create 0 template_table 1 pattern_template 0 actions_template 0 postpone 0 pattern eth / ipv4 / udp / end actions queue index 1 / end
//pull the completion
flow pull 0 queue 0


"""